"""API serializers for the HarmonizedSystemCodes plugin.

In practice, you would define your custom serializers here.

Ref: https://www.django-rest-framework.org/api-guide/serializers/
"""

from company.serializers import CompanySerializer
from InvenTree.serializers import InvenTreeModelSerializer
from part.serializers import CategorySerializer

from .models import HarmonizedSystemCode


class HarmonizedSystemCodeSerializer(InvenTreeModelSerializer):
    """Serializer for the HarmonizedSystemCode model."""

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
            # Detail serializers
            "category_detail",
            "customer_detail",
        ]

    category_detail = CategorySerializer(source="category", many=False, read_only=True)

    customer_detail = CompanySerializer(source="customer", many=False, read_only=True)
