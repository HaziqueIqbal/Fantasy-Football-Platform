from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from fantasyfootball.player.v1.serializers import PlayerSerializer
from fantasyfootball.team.models import Team


class TeamSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")
    owner_name = serializers.SerializerMethodField()
    total_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    player_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "owner",
            "owner_email",
            "owner_name",
            "budget",
            "total_value",
            "player_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "budget", "created_at", "updated_at")

    @extend_schema_field(serializers.CharField())
    def get_owner_name(self, obj: Team) -> str:
        return obj.owner.full_name

    @extend_schema_field(serializers.IntegerField())
    def get_player_count(self, obj: Team) -> int:
        return obj.players.count()


class TeamDetailSerializer(TeamSerializer):
    players = PlayerSerializer(many=True, read_only=True)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ("players",)


class TeamListSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")
    total_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "owner_email",
            "budget",
            "total_value",
            "created_at",
        )
