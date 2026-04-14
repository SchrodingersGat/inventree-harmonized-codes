"""API views for the HarmonizedSystemCodes plugin.

Ref: https://www.django-rest-framework.org/api-guide/views/
"""

from rest_framework import permissions
import django_filters.rest_framework.filters as rest_filters
from django_filters.rest_framework.filterset import FilterSet

import part.models as part_models

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from InvenTree.permissions import RolePermission

from .models import HarmonizedSystemCode
from .serializers import HarmonizedSystemCodeSerializer


class HarominzedSystemCodeMixin:
    """Mixin class for the API views."""

    queryset = HarmonizedSystemCode.objects.all()
    serializer_class = HarmonizedSystemCodeSerializer

    role_required = "sales_order"

    permission_classes = [permissions.IsAuthenticated, RolePermission]


class HarmonizedSystemCodeFilter(FilterSet):
    """Filter class for the HarmonizedSystemCode model."""

    class Meta:
        """Meta options for the filter."""

        model = HarmonizedSystemCode
        fields = [
            "category",
            "customer",
            "active",
        ]

    # Filter to show only codes associated with a particular category (or above)
    in_category = rest_filters.ModelChoiceFilter(
        queryset=part_models.PartCategory.objects.all(),
        method="filter_in_category",
    )

    def filter_in_category(self, queryset, name, category):
        """Limit the queryset to codes associated with a particular category (or above)."""

        if not category:
            return queryset

        # Get the category and all subcategories
        return queryset.filter(
            category__in=list(category.get_ancestors(include_self=True))
        )


class HarmonizedSystemCodeList(
    HarominzedSystemCodeMixin, DataExportViewMixin, ListCreateAPI
):
    """API endpoint for listing or creating Harmonized System Codes."""

    filter_backends = SEARCH_ORDER_FILTER
    filterset_class = HarmonizedSystemCodeFilter

    ordering_fields = ["active", "code", "category", "customer"]

    search_fields = [
        "code",
        "category__name",
        "category__description",
        "customer__name",
        "customer__description",
    ]


class HarmonizedSystemCodeDetail(HarominzedSystemCodeMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for retrieving, updating, or deleting a Harmonized System Code."""

    queryset = HarmonizedSystemCode.objects.all()
    serializer_class = HarmonizedSystemCodeSerializer
