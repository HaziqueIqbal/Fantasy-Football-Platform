import logging
import random
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from fantasyfootball.common.exceptions import (
    BadRequestException,
    PermissionDeniedException,
    ResourceNotFoundException,
)
from fantasyfootball.common.utils import format_response
from fantasyfootball.transaction.models import Transaction
from fantasyfootball.transfer.filters import TransferListingFilter
from fantasyfootball.transfer.models import TransferListing

from .serializers import TransferListingCreateSerializer, TransferListingSerializer

logger = logging.getLogger(__name__)


class TransferMarketView(ListAPIView):
    """Browse all active transfer listings."""

    permission_classes = [IsAuthenticated]
    serializer_class = TransferListingSerializer
    filterset_class = TransferListingFilter
    search_fields = ["player__first_name", "player__last_name", "player__country"]
    ordering_fields = ["asking_price", "created_at"]
    ordering = ["-created_at"]

    @extend_schema(tags=["Transfer Market"], summary="Browse the transfer market")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            TransferListing.objects.filter(is_active=True)
            .select_related("player__team", "seller")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return format_response(
            data=paginated.data,
            message="Transfer market retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class ListPlayerForSaleView(APIView):
    """List a player from your team on the transfer market."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TransferListingCreateSerializer,
        responses={201: TransferListingSerializer},
        tags=["Transfer Market"],
        summary="List a player for sale",
    )
    def post(self, request):
        serializer = TransferListingCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        listing = serializer.save(seller=request.user)
        return format_response(
            data=TransferListingSerializer(listing).data,
            message="Player listed for sale successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class TransferListingDetailView(APIView):
    """Remove your own active transfer listing (soft delete)."""

    permission_classes = [IsAuthenticated]

    def _get_listing(self, pk):
        try:
            return TransferListing.objects.select_related(
                "player", "seller"
            ).get(pk=pk, is_active=True)
        except TransferListing.DoesNotExist:
            raise ResourceNotFoundException("Active transfer listing not found.")

    @extend_schema(
        responses={200: OpenApiResponse(description="Listing removed.")},
        tags=["Transfer Market"],
        summary="Remove a transfer listing",
        description="Marks the listing as inactive (is_active=False). Only the seller can do this.",
    )
    def delete(self, request, pk):
        listing = self._get_listing(pk)
        if listing.seller != request.user:
            raise PermissionDeniedException(
                "You can only remove your own transfer listings."
            )
        listing.is_active = False
        listing.save(update_fields=["is_active", "updated_at"])
        logger.info("Transfer listing %s removed by %s", pk, request.user.email)
        return format_response(
            data=None,
            message="Transfer listing removed successfully.",
            status_code=status.HTTP_200_OK,
        )


class BuyPlayerView(APIView):
    """Purchase a player listed on the transfer market."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: inline_serializer(
                "BuyPlayerResponse",
                fields={
                    "transaction_id": drf_serializers.UUIDField(),
                    "player": drf_serializers.CharField(),
                    "new_player_value": drf_serializers.DecimalField(max_digits=15, decimal_places=2),
                    "transfer_amount": drf_serializers.DecimalField(max_digits=15, decimal_places=2),
                    "buyer_remaining_budget": drf_serializers.DecimalField(max_digits=15, decimal_places=2),
                },
            )
        },
        tags=["Transfer Market"],
        summary="Buy a listed player",
        description=(
            "Atomically: deducts price from buyer, credits seller, moves player, "
            "increases player value by a random 10–100%, records Transaction."
        ),
    )
    def post(self, request, pk):
        with transaction.atomic():
            return self._execute_purchase(request, pk)

    def _execute_purchase(self, request, pk):
        try:
            listing = TransferListing.objects.select_related(
                "player__team", "seller__team"
            ).get(pk=pk, is_active=True)
        except TransferListing.DoesNotExist:
            raise ResourceNotFoundException("Active transfer listing not found.")

        buyer = request.user
        seller = listing.seller
        player = listing.player
        price = listing.asking_price

        if buyer == seller:
            raise BadRequestException("You cannot buy your own player.")

        try:
            buyer_team = buyer.team
        except Exception:
            raise BadRequestException("You do not have a team.")

        if buyer_team.budget < price:
            raise BadRequestException(
                f"Insufficient budget. You have ${buyer_team.budget:,.2f} "
                f"but need ${price:,.2f}."
            )

        seller_team = player.team

        buyer_team.budget -= price
        buyer_team.save(update_fields=["budget", "updated_at"])

        if seller_team:
            seller_team.budget += price
            seller_team.save(update_fields=["budget", "updated_at"])

        player.team = buyer_team
        increase_pct = random.randint(
            settings.TRANSFER_VALUE_INCREASE_MIN,
            settings.TRANSFER_VALUE_INCREASE_MAX,
        )
        new_value = player.value * (1 + Decimal(str(increase_pct)) / 100)
        player.value = new_value.quantize(Decimal("0.01"))
        player.save(update_fields=["team", "value", "updated_at"])

        listing.is_active = False
        listing.save(update_fields=["is_active", "updated_at"])

        transaction_record = Transaction.objects.create(
            player=player,
            from_team=seller_team,
            to_team=buyer_team,
            seller=seller,
            buyer=buyer,
            transfer_amount=price,
            transfer_listing=listing,
        )

        logger.info(
            "Transfer complete: player %s from %s to %s for $%s",
            player, seller.email, buyer.email, price,
        )

        return format_response(
            data={
                "transaction_id": str(transaction_record.id),
                "player": str(player),
                "new_player_value": str(player.value),
                "transfer_amount": str(price),
                "buyer_remaining_budget": str(buyer_team.budget),
            },
            message="Player purchased successfully.",
            status_code=status.HTTP_200_OK,
        )
