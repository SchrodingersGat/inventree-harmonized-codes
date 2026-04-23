"""Custom model definitions for the HarmonizedSystemCodes plugin.

This file is where you can define any custom database models.

- Any models defined here will require database migrations to be created.
- Don't forget to register your models in the admin interface if needed!
"""

from django.db import models
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from part.models import PartCategory
from company.models import Company


class HarmonizedSystemCode(models.Model):
    """Model representing a Harmonized System Code."""

    class Meta:
        """Meta options for the model."""

        app_label = "harmonized_system_codes"
        verbose_name = _("Harmonized System Code")
        verbose_name_plural = _("Harmonized System Codes")

    @classmethod
    def check_user_permission(cls, user, permission) -> bool:
        """Custom permission check for Harmonized System Codes.

        This method can be used to implement custom permission logic for this model.
        For example, you might want to restrict access based on user groups, or other criteria.

        Arguments:
            user: The user for whom the permission check is being performed
            permission: The type of permission being checked (e.g. 'view', 'add', 'change', 'delete')
        """

        from plugin.registry import registry
        from . import PLUGIN_SLUG

        plugin = registry.get_plugin(PLUGIN_SLUG)

        if not plugin:
            raise ValidationError(
                _("Harmonized System Codes plugin not found in registry.")
            )

        group_id = plugin.get_setting("USER_GROUP")

        try:
            group = Group.objects.get(id=group_id) if group_id else None
        except (ValueError, Group.DoesNotExist):
            # Group does not exist, allow access to any user
            return True

        if not group:
            # Group does not exist, allow access to any user
            return True

        # Check if the user belongs to the specified group
        return group in user.groups.all()

    def save(self, *args, **kwargs):
        """Custom save method to enforce any constraints or perform actions before saving."""

        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Custom validation logic for the model."""

        # Ensure the code is unique for the given category and customer
        if (
            HarmonizedSystemCode.objects.filter(
                category=self.category,
                customer=self.customer,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                _(
                    "A Harmonized System Code with this category, and customer already exists."
                )
            )

        self.validate_country_code()

    def validate_country_code(self):
        """Run validation on the country field.

        If a SelectionList is provided for the country field,
        ensure the provided country value is valid.
        """

        from plugin.registry import registry
        from . import PLUGIN_SLUG

        if not self.country:
            return

        hc_plugin = registry.get_plugin(PLUGIN_SLUG)

        if not hc_plugin:
            raise ValidationError(
                _("Harmonized System Codes plugin not found in registry.")
            )

        country_list = hc_plugin.get_country_list()

        # No country list - no further validation needed
        if not country_list:
            return

        # Exact match - no further validation needed
        if country_list.entries.filter(active=True, value=self.country).exists():
            return

        # Try case insensitive match - if this works, update the country code to match the selection list
        inexact_matches = country_list.entries.filter(
            active=True, value__iexact=self.country
        )

        if inexact_matches.count() == 1:
            self.country = inexact_matches.first().value
            return

        # No match - raise validation error with the name of the selection list
        name = country_list.name
        raise ValidationError({
            "country": _(f"Country code does not exist in the {name} selection list")
        })

    code = models.CharField(
        max_length=20,
        verbose_name=_("Code"),
        help_text=_("Harmonized System Code"),
    )

    description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Description of the Harmonized System Code"),
    )

    category = models.ForeignKey(
        PartCategory,
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
        help_text=_("Part category associated with this HS code"),
        related_name="hs_codes",
    )

    customer = models.ForeignKey(
        Company,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Customer"),
        help_text=_("Customer associated with this HS code"),
        related_name="hs_codes",
    )

    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Country"),
        help_text=_("Country associated with this HS code"),
    )

    notes = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Additional notes about the HS code"),
    )

    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this HS code is active"),
    )
