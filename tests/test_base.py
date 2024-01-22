import pytest
from mock_module.administration.mock import MockView, MockViewAlternate

from invenio_administration.views.base import AdminView


class TestCustomView(AdminView):
    name = "Test Custom View"
    extension_name = "test-custom-view"
    category = "Test category"


def test_view_registration_from_entry_point(
    mock_extension, current_admin_core, test_app
):
    """Test view registration from entry point."""
    # Validate extension is registered
    assert mock_extension is not None

    # Assert view registration
    registered_view = list(
        filter(lambda x: x.view_class == MockView, current_admin_core.views)
    )
    assert len(registered_view) == 1
    assert registered_view[0].view_class == MockView

    # Assert url is registered
    custom_view_rule = [
        x
        for x in test_app.url_map.iter_rules()
        if x.rule == f"{current_admin_core.url}/{MockView.url}"
    ]
    assert len(custom_view_rule) == 1

    # Validate that two views are registered from the same module
    # Assert view registration
    registered_view = list(
        filter(lambda x: x.view_class == MockViewAlternate, current_admin_core.views)
    )
    assert len(registered_view) == 1
    assert registered_view[0].view_class == MockViewAlternate


def test_view_registration_duplicated(current_admin_ext, test_app, mock_extension_name):
    """Test duplicated view registration."""
    dup_cls = MockView
    dup_cls.extension_name = mock_extension_name

    with pytest.raises(ValueError):
        current_admin_ext.register_view(
            MockView, extension_name=dup_cls.extension_name, app=test_app
        )


def test_view_registration_url_naming(test_app, current_admin_core):
    """Test view registration urls with spaces."""
    # Get registered url from app's url Map
    view_filter = [
        v
        for v in current_admin_core.views
        if v.view_class.name == MockViewAlternate.name
    ]
    assert len(view_filter) == 1

    view = view_filter[0]

    custom_view_rule = [
        x
        for x in test_app.url_map.iter_rules()
        if x.endpoint == f"{current_admin_core.endpoint}.{view.view_class.name}"
    ]

    assert len(custom_view_rule) == 1

    registered_url = custom_view_rule[0].rule

    # Test that the registered url is the view's name without whitespaces, lower cased.
    expected_url = "{}/{}".format(
        current_admin_core.url, MockViewAlternate.name.replace(" ", "_").lower()
    )
    assert registered_url == expected_url


def test_view_registration_url_explicit(test_app, current_admin_core):
    """Test url registration for explicit set urls."""
    custom_view_rule = [
        x
        for x in test_app.url_map.iter_rules()
        if x.rule == f"{current_admin_core.url}/{MockView.url}"
    ]
    assert len(custom_view_rule) == 1
