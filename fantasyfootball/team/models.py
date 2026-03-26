from decimal import Decimal

from django.conf import settings
from django.db import models

from fantasyfootball.common.mixins import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team",
        db_index=True,
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("5000000.00"),
    )

    class Meta:
        db_table = "teams"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        """Sum of all player values in the team."""
        result = self.players.aggregate(
            total=models.Sum("value")
        )
        return result["total"] or Decimal("0")
