import django_filters

from .models import Player


class PlayerFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    country = django_filters.CharFilter(lookup_expr="icontains")
    position = django_filters.ChoiceFilter(choices=Player.Position.choices)
    team = django_filters.UUIDFilter(field_name="team__id")
    min_value = django_filters.NumberFilter(field_name="value", lookup_expr="gte")
    max_value = django_filters.NumberFilter(field_name="value", lookup_expr="lte")

    class Meta:
        model = Player
        fields = ["first_name", "last_name", "country", "position", "team", "min_value", "max_value"]
