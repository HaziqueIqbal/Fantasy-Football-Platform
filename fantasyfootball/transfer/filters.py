from django.db import models
import django_filters

from .models import TransferListing


class TransferListingFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="asking_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="asking_price", lookup_expr="lte")
    position = django_filters.CharFilter(field_name="player__position", lookup_expr="iexact")
    player_name = django_filters.CharFilter(method="filter_player_name")
    country = django_filters.CharFilter(field_name="player__country", lookup_expr="icontains")

    class Meta:
        model = TransferListing
        fields = ["min_price", "max_price", "position", "player_name", "country"]

    def filter_player_name(self, queryset, name, value):
        return queryset.filter(
            models.Q(player__first_name__icontains=value)
            | models.Q(player__last_name__icontains=value)
        )
