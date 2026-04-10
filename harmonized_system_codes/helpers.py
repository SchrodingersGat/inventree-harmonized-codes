"""Helper function for the HarmonizedSystemCodes plugin."""

from typing import Optional

from .models import HarmonizedSystemCode


def get_harmonized_code(
    part, customer=None, country: Optional[str] = None
) -> HarmonizedSystemCode:
    """Retrieve the harmonized system code for a given part and optional customer.

    Arguments:
        part: The part instance for which to retrieve the HS code.
        customer: (Optional) The company instance to filter the HS code by customer.
        country: (Optional) The country code to filter the HS code by country.

    Returns:
        HarmonizedSystemCode instance if found, else None.

    Notes:
        - The most "specific" harmonized code should be returned where avaliable
        - A match against the category and customer should take precedence over a generic category match
        - If a country code is provided, codes matching that country should be prioritised over those without a country code
    """

    category = part.category

    # No category, no code
    if not category:
        return None

    # Work up the category tree to find a matching code
    categories = category.get_ancestors(include_self=True)

    hs_codes = HarmonizedSystemCode.objects.filter(active=True, category__in=categories)

    # Order by category level (deepest level first)
    hs_codes = hs_codes.order_by("-category__level")

    # First, try matching against a Company (if provided)
    # A company-specific code will override a generic one
    if customer:
        company_hs_codes = hs_codes.filter(customer=customer)

        # If customer and country are provided, then filter by country as well
        if country:
            country_hs_codes = company_hs_codes.filter(country=country)
            if country_hs_codes.exists():
                return country_hs_codes.first()

        if company_hs_codes.exists():
            return company_hs_codes.first()

    # Next, try matching against the country code (if provided)
    # A country-specific code will override a generic one
    if country:
        country_hs_codes = hs_codes.filter(country=country)
        if country_hs_codes.exists():
            return country_hs_codes.first()

    # Return the first matching code, or None if not found
    return hs_codes.first()
