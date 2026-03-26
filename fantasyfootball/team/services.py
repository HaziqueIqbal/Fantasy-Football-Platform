import logging
import random
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from fantasyfootball.player.models import Player

from .models import Team

logger = logging.getLogger(__name__)

FIRST_NAMES = [
    "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas",
    "Henry", "Alexander", "Mason", "Ethan", "Daniel", "Jacob", "Logan", "Jackson",
    "Sebastian", "Jack", "Aiden", "Owen", "Samuel", "Mateo", "Joseph", "Levi",
    "David", "Carter", "Wyatt", "Julian", "John", "Ezra",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
]

COUNTRIES = [
    "Brazil", "Argentina", "France", "Germany", "Spain", "England", "Italy",
    "Portugal", "Netherlands", "Belgium", "Uruguay", "Colombia", "Chile",
    "Croatia", "Denmark", "Sweden", "Poland", "Mexico", "USA", "Japan",
]


class TeamService:
    @staticmethod
    @transaction.atomic
    def create_team_for_user(user):
        """
        Create a team with 20 players for a newly registered user:
          - 3 goalkeepers
          - 5 defenders
          - 6 midfielders
          - 6 attackers
        Initial budget: $5,000,000. Each player value: $1,000,000.
        """
        distribution = settings.PLAYER_DISTRIBUTION
        initial_budget = Decimal(str(settings.TEAM_INITIAL_BUDGET))
        initial_player_value = Decimal(str(settings.PLAYER_VALUE_INITIAL if hasattr(settings, 'PLAYER_VALUE_INITIAL') else settings.PLAYER_INITIAL_VALUE))

        team_name = f"{user.first_name} {user.last_name}'s FC"
        counter = 1
        base_name = team_name
        while Team.objects.filter(name=team_name).exists():
            team_name = f"{base_name} {counter}"
            counter += 1

        team = Team.objects.create(
            name=team_name,
            owner=user,
            budget=initial_budget,
        )

        players_to_create = []
        for position, count in distribution.items():
            for _ in range(count):
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                country = random.choice(COUNTRIES)
                players_to_create.append(
                    Player(
                        first_name=first_name,
                        last_name=last_name,
                        country=country,
                        position=position,
                        value=initial_player_value,
                        team=team,
                    )
                )

        Player.objects.bulk_create(players_to_create)
        logger.info("Created team '%s' with %d players for user %s", team.name, len(players_to_create), user.email)
        return team
