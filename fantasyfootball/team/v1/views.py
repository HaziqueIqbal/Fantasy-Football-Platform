import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from fantasyfootball.common.exceptions import ResourceNotFoundException
from fantasyfootball.common.utils import format_response
from fantasyfootball.team.models import Team

from .serializers import TeamDetailSerializer, TeamListSerializer

logger = logging.getLogger(__name__)


class MyTeamView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: TeamDetailSerializer},
        tags=["Teams"],
        summary="Get my team",
        description="Returns the authenticated user's team with all players.",
    )
    def get(self, request):
        try:
            team = Team.objects.prefetch_related("players").get(owner=request.user)
        except Team.DoesNotExist:
            raise ResourceNotFoundException("You do not have a team yet.")

        serializer = TeamDetailSerializer(team)
        return format_response(
            data=serializer.data,
            message="Team retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class TeamDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: TeamDetailSerializer},
        tags=["Teams"],
        summary="Get team by ID",
    )
    def get(self, request, pk):
        try:
            team = Team.objects.prefetch_related("players").get(pk=pk)
        except Team.DoesNotExist:
            raise ResourceNotFoundException("Team not found.")

        serializer = TeamDetailSerializer(team)
        return format_response(
            data=serializer.data,
            message="Team retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class TeamListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamListSerializer
    search_fields = ["name", "owner__email", "owner__first_name", "owner__last_name"]
    ordering_fields = ["name", "budget", "created_at"]
    ordering = ["-created_at"]

    @extend_schema(tags=["Teams"], summary="List all teams")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Team.objects.select_related("owner").all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return format_response(
            data=paginated.data,
            message="Teams retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
