"""Support harmonized system codes against sales orders"""

from django.contrib.auth.models import Group

from plugin import InvenTreePlugin

from plugin.mixins import (
    AppMixin,
    EventMixin,
    ReportMixin,
    SettingsMixin,
    UrlsMixin,
    UserInterfaceMixin,
)

from . import PLUGIN_SLUG, PLUGIN_VERSION


class HarmonizedSystemCodes(
    AppMixin,
    EventMixin,
    ReportMixin,
    SettingsMixin,
    UrlsMixin,
    UserInterfaceMixin,
    InvenTreePlugin,
):
    """HarmonizedSystemCodes - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "Harmonized System Codes"
    NAME = "HarmonizedSystemCodes"
    DESCRIPTION = "Support harmonized system codes against sales orders"
    SLUG = PLUGIN_SLUG
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Oliver Walters"
    WEBSITE = "https://github.com/SchrodingersGat/inventree-harmoized-codes"
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    MIN_VERSION = "1.3.1"

    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/settings/
    SETTINGS = {
        # Define your plugin settings here...
        "USER_GROUP": {
            "name": "User Group",
            "description": "Group with access to harmonized system codes",
            "model": "auth.group",
        },
        "COUNTRY_LIST": {
            "name": "Country List",
            "description": "Selection list of country codes",
            "model": "common.selectionlist",
            "model_filters": {
                "active": True,
            },
        },
    }

    def get_country_list(self):
        """Return the SelectionList instance for determining country codes."""

        if country_list_id := self.get_setting("COUNTRY_LIST", backup_value=None):
            from common.models import SelectionList

            try:
                return SelectionList.objects.get(id=country_list_id)
            except SelectionList.DoesNotExist:
                return None

        return None

    # Respond to InvenTree events (from EventMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/event/
    def wants_process_event(self, event: str) -> bool:
        """Return True if the plugin wants to process the given event."""
        # TODO: Handle custom events here when line items are created / modified
        return False

    def process_event(self, event: str, *args, **kwargs) -> None:
        """Process the provided event."""
        ...

    def add_report_context(
        self, report_instance, model_instance, request, context, **kwargs
    ):
        """Add custom context data to a report rendering context."""
        ...

    # Custom URL endpoints (from UrlsMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/urls/
    def setup_urls(self):
        """Configure custom URL endpoints for this plugin."""
        from django.urls import path
        from .views import HarmonizedSystemCodeList, HarmonizedSystemCodeDetail

        return [
            # Provide path to a simple custom view - replace this with your own views
            path(
                "<int:pk>/",
                HarmonizedSystemCodeDetail.as_view(),
                name="harmonizedsystemcode-detail",
            ),
            path(
                "", HarmonizedSystemCodeList.as_view(), name="harmonizedsystemcode-list"
            ),
        ]

    # User interface elements (from UserInterfaceMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/ui/

    def display_codes_panel(self, request, context: dict, **kwargs):
        """Determine whether to display the harmonized system codes panel."""

        from company.models import Company

        target_model = context.get("target_model", None)
        target_id = context.get("target_id", None)

        # Always display on the admin center
        if target_model == "admincenter":
            return True

        # Always display on the "sales" index page
        if target_model == "sales" and target_id is None:
            return True

        # Display for customers
        if target_model == "company" and target_id:
            try:
                company = Company.objects.filter(pk=target_id).first()
                if company and company.is_customer:
                    return True
            except (Company.DoesNotExist, ValueError):
                return False

        # Display for part categories
        if target_model == "partcategory" and target_id:
            return True

        # Default: do not display
        return False

    # Custom UI panels
    def get_ui_panels(self, request, context: dict, **kwargs):
        """Return a list of custom panels to be rendered in the InvenTree user interface."""

        panels = []

        user_valid = request.user and request.user.is_authenticated

        # Look at the group that the user is in
        if group_id := self.get_setting("USER_GROUP", backup_value=None):
            try:
                group = Group.objects.get(id=group_id)
                if not request.user.groups.filter(id=group.id).exists():
                    user_valid = False
            except Group.DoesNotExist:
                user_valid = False

        if not user_valid:
            return []

        if self.display_codes_panel(request, context, **kwargs):
            panels.append({
                "key": "harmonized-system-codes-panel",
                "title": "Harmonized Codes",
                "description": "Display harmonized system codes",
                "icon": "ti:flag-search:outline",
                "source": self.plugin_static_file(
                    "Panel.js:renderHarmonizedSystemCodesPanel"
                ),
                "context": {
                    # Provide additional context data to the panel
                    "settings": self.get_settings_dict(),
                },
            })

        return panels
