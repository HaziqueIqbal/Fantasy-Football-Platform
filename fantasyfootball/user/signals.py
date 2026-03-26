import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_team_for_new_user(sender, instance, created, **kwargs):
    """Automatically create a team with 20 players for every new user."""
    if created:
        from fantasyfootball.team.services import TeamService

        try:
            TeamService.create_team_for_user(instance)
            logger.info("Team created for user %s", instance.email)
        except Exception as exc:
            logger.error(
                "Failed to create team for user %s: %s", instance.email, exc
            )
