import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from fantasyfootball.common.utils import format_response
from fantasyfootball.transaction.filters import TransactionFilter
from fantasyfootball.transaction.models import Transaction

from .serializers import TransactionSerializer

logger = logging.getLogger(__name__)


class TransactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    ordering_fields = ["transfer_amount", "created_at"]
    ordering = ["-created_at"]

    @extend_schema(
        tags=["Transaction"],
        summary="List all transactions",
        description=(
            "Returns a paginated, filterable history of all completed player transfers. "
            "Filter by buyer, seller, from_team, to_team, min_amount, or max_amount. "
            "Order by transfer_amount or created_at."
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Transaction.objects.select_related(
            "player", "from_team", "to_team", "seller", "buyer"
        ).all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return format_response(
            data=paginated.data,
            message="Transaction history retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class TransactionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    lookup_field = "pk"

    @extend_schema(
        tags=["Transaction"],
        summary="Get transaction by ID",
        description="Returns the full details of a single completed transfer transaction by its UUID.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Transaction.objects.select_related(
            "player", "from_team", "to_team", "seller", "buyer"
        ).all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return format_response(
            data=serializer.data,
            message="Transaction retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
