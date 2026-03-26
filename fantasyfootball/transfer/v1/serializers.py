from rest_framework import serializers

from fantasyfootball.player.v1.serializers import PlayerSerializer
from fantasyfootball.transfer.models import TransferListing


class TransferListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferListing
        fields = ("id", "player", "asking_price", "is_active", "created_at")
        read_only_fields = ("id", "is_active", "created_at")

    def validate_asking_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Asking price must be greater than zero.")
        return value

    def validate_player(self, player):
        request = self.context["request"]
        if player.team is None or player.team.owner != request.user:
            raise serializers.ValidationError(
                "You can only list players from your own team."
            )
        if hasattr(player, "transfer_listing") and player.transfer_listing.is_active:
            raise serializers.ValidationError(
                "This player is already listed on the transfer market."
            )
        return player


class TransferListingSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    seller_email = serializers.ReadOnlyField(source="seller.email")

    class Meta:
        model = TransferListing
        fields = (
            "id",
            "player",
            "seller_email",
            "asking_price",
            "is_active",
            "created_at",
            "updated_at",
        )
