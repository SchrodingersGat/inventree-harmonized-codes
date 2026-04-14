"""API serializers for the HarmonizedSystemCodes plugin.

In practice, you would define your custom serializers here.

Ref: https://www.django-rest-framework.org/api-guide/serializers/
"""

from company.serializers import CompanySerializer
from importer.registry import register_importer
from InvenTree.mixins import DataImportExportSerializerMixin
from InvenTree.serializers import InvenTreeModelSerializer
from part.serializers import CategorySerializer

from .models import HarmonizedSystemCode


@register_importer()
class HarmonizedSystemCodeSerializer(
    DataImportExportSerializerMixin, InvenTreeModelSerializer
):
    """Serializer for the HarmonizedSystemCode model."""

    export_child_fields = [
        "customer_detail.name",
        "category_detail.pathstring",
    ]

    class Meta:
        """Meta options for the serializer."""

        model = HarmonizedSystemCode
        fields = [
            "pk",
            "code",
            "category",
            "country",
            "customer",
            "description",
            "notes",
            "active",
            # Detail serializers
            "category_detail",
            "customer_detail",
        ]

    category_detail = CategorySerializer(source="category", many=False, read_only=True)

    customer_detail = CompanySerializer(source="customer", many=False, read_only=True)
