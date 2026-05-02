from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Expedition, ExpeditionMember, ExpeditionStatus, MemberState
from .serializers import (
    ExpeditionSerializer, InviteMemberSerializer,
    ExpeditionMemberSerializer, ConfirmMemberSerializer,
    GetMembersSerializer
)
from .services import ExpeditionService


class ExpeditionViewSet(ModelViewSet):
    queryset = Expedition.objects.all()
    serializer_class = ExpeditionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        expedition = serializer.save(chief=self.request.user, status=ExpeditionStatus.DRAFT)
        ExpeditionService.send_event(
            expedition.id, "expedition_status", {"status": ExpeditionStatus.DRAFT}
        )

    def get_queryset(self):
        user = self.request.user

        return Expedition.objects.filter(
            Q(chief=user) |
            Q(members__user=user)
        ).distinct()

    @extend_schema(
        responses={
            200: OpenApiResponse(response=GetMembersSerializer)
        }
    )
    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        expedition = self.get_object()

        members = ExpeditionMember.objects.filter(expedition=expedition)
        serializer = ExpeditionMemberSerializer(members, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def ready(self, request, pk=None):
        expedition = self.get_object()

        try:
            expedition.set_ready(request.user)
            ExpeditionService.send_event(
                expedition.id, "expedition_status", {"status": ExpeditionStatus.READY}
            )

            return Response({"status": ExpeditionStatus.READY})

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["post"])
    def active(self, request, pk=None):
        expedition = self.get_object()

        try:
            expedition.set_active(request.user)
            ExpeditionService.send_event(
                expedition.id, "expedition_status", {"status": ExpeditionStatus.ACTIVE}
            )

            return Response({"status": ExpeditionStatus.ACTIVE})

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        expedition = self.get_object()

        try:
            expedition.set_finished(request.user)
            ExpeditionService.send_event(
                expedition.id, "expedition_status", {"status": ExpeditionStatus.FINISHED}
            )

            return Response({"status": ExpeditionStatus.FINISHED})

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @extend_schema(
        request=InviteMemberSerializer,
        responses={
            200: OpenApiResponse(description="Invite sent")
        }
    )
    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):
        expedition = self.get_object()

        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user_id = serializer.validated_data["target_user_id"]

        try:
            ExpeditionService.invite(
                expedition=expedition,
                user=request.user,
                target_user_id=target_user_id,
            )
            ExpeditionService.send_event(
                expedition.id, "member_invited", {"user_id": target_user_id}
            )

            return Response({"status": MemberState.INVITED})

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @extend_schema(
        request=ConfirmMemberSerializer,
        responses={
            200: OpenApiResponse(description="Confirmed")
        }
    )
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        expedition = self.get_object()

        member = get_object_or_404(ExpeditionMember, user=request.user, expedition=expedition)

        try:
            ExpeditionService.confirm(member, request.user)
            ExpeditionService.send_event(
                expedition.id, "member_confirmed", {"member_id": member.id}
            )

            return Response({"status": MemberState.CONFIRMED})

        except Exception as e:
            return Response({"error": str(e)}, status=400)
