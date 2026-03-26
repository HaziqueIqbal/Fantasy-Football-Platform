from typing import Optional

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from fantasyfootball.transaction.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    player_position = serializers.ReadOnlyField(source="player.position")
    buyer_email = serializers.ReadOnlyField(source="buyer.email")
    seller_email = serializers.ReadOnlyField(source="seller.email")
    from_team_name = serializers.SerializerMethodField()
    to_team_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "player",
            "player_name",
            "player_position",
            "from_team",
            "from_team_name",
            "to_team",
            "to_team_name",
            "seller",
            "seller_email",
            "buyer",
            "buyer_email",
            "transfer_amount",
            "transfer_listing",
            "created_at",
        )
        read_only_fields = fields

    @extend_schema_field(serializers.CharField())
    def get_player_name(self, obj: Transaction) -> str:
        return obj.player.full_name

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_from_team_name(self, obj: Transaction) -> Optional[str]:
        return obj.from_team.name if obj.from_team else None

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_to_team_name(self, obj: Transaction) -> Optional[str]:
        return obj.to_team.name if obj.to_team else None
