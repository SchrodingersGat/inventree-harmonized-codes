"""Custom template tags for the HarmonizedSystemCodes plugin."""

from typing import Optional

from django import template

register = template.Library()


@register.simple_tag
def harmonized_code(part, customer=None, country: Optional[str] = None):
    """Retrieve the Harmonized System Code for a given part and optional company.

    Arguments:
        part: The part instance for which to retrieve the HS code.
        customer: (Optional) The company instance to filter the HS code by customer.
        country: (Optional) The country code to filter the HS code by country.
    """
    from ..helpers import get_harmonized_code

    return get_harmonized_code(part, customer=customer, country=country)


@register.simple_tag
def harmonized_codes_for_country(country: str, active: Optional[bool] = True):
    """Retrieve a list of Harmonized System Code associated with a particular country.

    Arguments:
        country: The country code to filter the HS code by country.
    """
    from ..models import HarmonizedSystemCode

    codes = HarmonizedSystemCode.objects.filter(country=country)

    if active is not None:
        codes = codes.filter(active=active)

    return list(codes)


@register.simple_tag
def harmonized_codes_for_customer(customer, active: Optional[bool] = True):
    """Retrieve a list of Harmonized System Code associated with a particular customer.

    Arguments:
        customer: The company instance to filter the HS code by customer.
    """
    from ..models import HarmonizedSystemCode

    codes = HarmonizedSystemCode.objects.filter(customer=customer)

    if active is not None:
        codes = codes.filter(active=active)

    return list(codes)
