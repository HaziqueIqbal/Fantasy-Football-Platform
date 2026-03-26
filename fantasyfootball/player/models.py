from django.db import models

from fantasyfootball.common.mixins import BaseModel


class Player(BaseModel):
    class Position(models.TextChoices):
        GOALKEEPER = "goalkeeper", "Goalkeeper"
        DEFENDER = "defender", "Defender"
        MIDFIELDER = "midfielder", "Midfielder"
        ATTACKER = "attacker", "Attacker"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Unknown")
    position = models.CharField(
        max_length=20, choices=Position.choices, db_index=True
    )
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=1_000_000,
    )
    team = models.ForeignKey(
        "team.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
        db_index=True,
    )

    class Meta:
        db_table = "players"
        ordering = ["position", "last_name"]
        indexes = [
            models.Index(fields=["position"]),
            models.Index(fields=["team"]),
            models.Index(fields=["value"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
