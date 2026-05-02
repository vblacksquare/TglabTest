from rest_framework import serializers
from .models import Expedition, ExpeditionMember


class ExpeditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expedition
        fields = "__all__"
        read_only_fields = ("status", "created_at", "updated_at", "chief")


class ExpeditionMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpeditionMember
        fields = "__all__"
        read_only_fields = ("state", "invited_at", "confirmed_at")


class InviteMemberSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField()


class ConfirmMemberSerializer(serializers.Serializer):
    pass


class GetMembersSerializer(serializers.Serializer):
    members = ExpeditionMemberSerializer(many=True)
