import logging

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return format_response(
            data=serializer.data,
            message="Player retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
