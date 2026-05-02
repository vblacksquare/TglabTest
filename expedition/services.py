
from django.contrib.auth import get_user_model
from .models import ExpeditionMember, ExpeditionStatus, MemberState

from django.core.mail import send_mail
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


User = get_user_model()


class ExpeditionService:

    @staticmethod
    def send_event(expedition_id, event_type, payload):
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"expedition_{expedition_id}",
            {
                "type": "expedition_event",
                "data": {
                    "type": event_type,
                    "payload": payload
                }
            }
        )

    @staticmethod
    def invite(expedition, user, target_user_id):

        if expedition.status != ExpeditionStatus.DRAFT:
            raise Exception("Invites only in draft")

        if user != expedition.chief:
            raise Exception("Only chief can invite")

        target_user = User.objects.get(id=target_user_id)

        exists = ExpeditionMember.objects.filter(
            expedition=expedition,
            user=target_user
        ).exists()

        if exists:
            raise Exception("Already invited")

        link = f"http://127.0.0.1:8000/api/v1/expedition/{expedition.id}/confirm/"

        send_mail(
            "Confirm invitation",
            f"Click: {link}",
            settings.EMAIL_HOST_USER,
            [target_user.email],
        )

        ExpeditionMember.objects.create(
            expedition=expedition,
            user=target_user,
            state=MemberState.INVITED
        )

    @staticmethod
    def confirm(member, user):
        if member.user != user:
            raise Exception("Only invited user can confirm")

        if member.state != MemberState.INVITED:
            raise Exception("Invalid state")

        member.state = MemberState.CONFIRMED
        member.save(update_fields=["state"])
