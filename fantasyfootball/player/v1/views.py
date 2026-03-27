import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from fantasyfootball.common.utils import format_response
from fantasyfootball.player.filters import PlayerFilter
from fantasyfootball.player.models import Player

from .serializers import PlayerSerializer

logger = logging.getLogger(__name__)


class PlayerListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerSerializer
    filterset_class = PlayerFilter
    search_fields = ["first_name", "last_name", "country"]
    ordering_fields = ["value", "position", "last_name", "created_at"]
    ordering = ["position", "last_name"]

    @extend_schema(
        tags=["Player"],
        summary="List all players",
        description=(
            "Returns a paginated list of all players across all teams. "
            "Filter by position, country, team, min_value, max_value, first_name, or last_name. "
            "Search across first_name, last_name, and country. "
            "Order by value, position, last_name, or created_at."
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Player.objects.select_related("team").all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated_response = self.get_paginated_response(serializer.data)
        return format_response(
            data=paginated_response.data,
            message="Players retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PlayerDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerSerializer
    queryset = Player.objects.select_related("team").all()
    lookup_field = "pk"

    @extend_schema(
        tags=["Player"],
        summary="Get player by ID",
        description="Returns the full details of a single player by their UUID, including their current team and value.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return format_response(
            data=serializer.data,
            message="Player retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
