from django.contrib import admin

from .models import TransferListing


@admin.register(TransferListing)
class TransferListingAdmin(admin.ModelAdmin):
    list_display = ("player", "seller", "asking_price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("player__first_name", "player__last_name", "seller__email")
    ordering = ("-created_at",)
    list_select_related = ("player", "seller")
