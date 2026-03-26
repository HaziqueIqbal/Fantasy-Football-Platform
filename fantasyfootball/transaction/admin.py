from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "seller", "buyer", "transfer_amount", "created_at")
    list_filter = ()
    search_fields = (
        "player__first_name", "player__last_name",
        "seller__email", "buyer__email",
    )
    ordering = ("-created_at",)
    list_select_related = ("player", "seller", "buyer", "from_team", "to_team")
    readonly_fields = [f.name for f in Transaction._meta.get_fields()]

    def has_delete_permission(self, request, obj=None):
        return False
