import django_filters

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    buyer = django_filters.UUIDFilter(field_name="buyer__id")
    seller = django_filters.UUIDFilter(field_name="seller__id")
    min_amount = django_filters.NumberFilter(field_name="transfer_amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="transfer_amount", lookup_expr="lte")
    from_team = django_filters.UUIDFilter(field_name="from_team__id")
    to_team = django_filters.UUIDFilter(field_name="to_team__id")

    class Meta:
        model = Transaction
        fields = ["buyer", "seller", "min_amount", "max_amount", "from_team", "to_team"]
