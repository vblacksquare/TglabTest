
from django.utils import timezone

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


User = get_user_model()


class ExpeditionStatus(models.TextChoices):
    DRAFT = "draft"
    READY = "ready"
    ACTIVE = "active"
    FINISHED = "finished"


class MemberState(models.TextChoices):
    INVITED = "invited"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Expedition(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExpeditionStatus.choices,
        default=ExpeditionStatus.DRAFT,
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)

    capacity = models.PositiveIntegerField()

    chief = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="led_expeditions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_be_ready(self) -> tuple[bool, str]:
        if self.status != ExpeditionStatus.DRAFT:
            return False, "Only such transition may be: draft -> ready"

        return True, None

    def can_be_active(self) -> tuple[bool, str]:
        if self.status != ExpeditionStatus.READY:
            return False, "Only such transition may be: ready -> active"

        now = timezone.now()

        confirmed_count = self.members.filter(
            state=MemberState.CONFIRMED
        ).count()

        if self.start_at > now:
            return False, "Can't start expedition before start_at time"

        if confirmed_count < 2:
            return False, "Minimum of members is 2"

        if confirmed_count > self.capacity:
            return False, "Members count is more than capacity"

        active_conflicts = ExpeditionMember.objects.filter(
            user__in=self.members.filter(state=MemberState.CONFIRMED).values("user"),
            expedition__status=ExpeditionStatus.ACTIVE
        ).exclude(expedition=self).exists()

        if active_conflicts:
            return False, "Some of users are in an active expedition"

        return True, None

    def can_be_finished(self) -> tuple[bool, str]:
        if self.status != ExpeditionStatus.ACTIVE:
            return False, "Only such transition may be: active -> finished"

        return True, None

    def set_ready(self, user):
        if user != self.chief:
            raise ValidationError("Only chief can change status")

        is_activated, reason = self.can_be_ready()

        if not is_activated:
            raise ValidationError(f"Cannot ready expeditiont: {reason}")

        self.status = ExpeditionStatus.READY
        self.save(update_fields=["status"])

    def set_active(self, user):
        if user != self.chief:
            raise ValidationError("Only chief can start expedition")

        is_activated, reason = self.can_be_active()

        if not is_activated:
            raise ValidationError(f"Cannot activate expedition: {reason}")

        self.status = ExpeditionStatus.ACTIVE
        self.save(update_fields=["status"])

    def set_finished(self, user):
        if user != self.chief:
            raise ValidationError("Only chief can finish expedition")

        is_activated, reason = self.can_be_finished()

        if not is_activated:
            raise ValidationError(f"Cannot finish expedition: {reason}")

        self.status = ExpeditionStatus.FINISHED
        self.save(update_fields=["status"])


class ExpeditionMember(models.Model):
    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expedition_memberships",
    )

    state = models.CharField(
        max_length=20,
        choices=MemberState.choices,
        default=MemberState.INVITED,
    )

    invited_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["expedition", "user"],
                name="unique_expedition_member"
            )
        ]
