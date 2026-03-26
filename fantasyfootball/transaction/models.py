from django.conf import settings
from django.db import models

from fantasyfootball.common.mixins import BaseModel


class Transaction(BaseModel):
    """A completed player transfer record. Never deleted."""

    player = models.ForeignKey(
        "player.Player",
        on_delete=models.PROTECT,
        related_name="transactions",
        db_index=True,
    )
    from_team = models.ForeignKey(
        "team.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outgoing_transactions",
        db_index=True,
    )
    to_team = models.ForeignKey(
        "team.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_transactions",
        db_index=True,
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sold_transactions",
        db_index=True,
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bought_transactions",
        db_index=True,
    )
    transfer_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transfer_listing = models.OneToOneField(
        "transfer.TransferListing",
        on_delete=models.PROTECT,
        related_name="transaction",
    )

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["buyer", "created_at"]),
            models.Index(fields=["seller", "created_at"]),
        ]

    def __str__(self):
        return f"Transaction {self.id}: {self.player} | ${self.transfer_amount}"

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Transactions cannot be deleted.")
