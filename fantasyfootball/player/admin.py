from django.contrib import admin

from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "country", "value", "team", "created_at")
    list_filter = ("position", "country")
    search_fields = ("first_name", "last_name", "country")
    ordering = ("position", "last_name")
    list_select_related = ("team",)
