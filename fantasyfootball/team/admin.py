from django.contrib import admin

from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "budget", "player_count", "created_at")
    search_fields = ("name", "owner__email")
    ordering = ("-created_at",)
    list_select_related = ("owner",)

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = "Players"
