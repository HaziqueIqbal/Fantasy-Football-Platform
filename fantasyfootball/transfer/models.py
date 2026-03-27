from django.conf import settings
from django.db import models

from fantasyfootball.common.mixins import BaseModel


class TransferListing(BaseModel):
    """A player listed on the transfer market."""

    player = models.ForeignKey(
        "player.Player",
        on_delete=models.CASCADE,
        related_name="transfer_listings",
        db_index=True,
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transfer_listings",
        db_index=True,
    )
    asking_price = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "transfer_listings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "created_at"]),
        ]

    def __str__(self):
        return f"{self.player} | {self.asking_price} | active={self.is_active}"
