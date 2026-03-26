from typing import Optional

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from fantasyfootball.player.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "country",
            "position",
            "value",
            "team",
            "team_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "value", "team", "created_at", "updated_at")

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj: Player) -> str:
        return obj.full_name

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_team_name(self, obj: Player) -> Optional[str]:
        return obj.team.name if obj.team else None
