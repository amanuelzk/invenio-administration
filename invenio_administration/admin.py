# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Administration core admin module."""

from flask import Blueprint
from flask_menu import current_menu
from werkzeug.utils import import_string

from invenio_administration.menu import AdminMenu

from .views.base import AdminResourceListView, AdminView


class Administration:
    """Admin views core manager."""

    def __init__(
        self,
        app=None,
        name=None,
        url=None,
        ui_endpoint=None,
        base_template=None,
    ):
        """Constructor.

        :param app: flask application
        :param name: application name, defaults to "Admin"
        :param url: base admin url to register the dashboard view and subviews
        :param dashboard_view: home page view
        :param ui_endpoint: base UI endpoint,
                     leaves flexibility to implement two different admin apps,
                     or to provide custom endpoint
        :param base_template: base admin template.
                     Defaults to "admin/base.html"
        """
        super().__init__()

        self.app = app
        self._views = []
        self._menu = AdminMenu()
        self._menu_key = "admin_navigation"
        self.blueprint = None

        if name is None:
            name = "Administration"
        self.name = name

        self.dashboard_view_class = self.load_admin_dashboard(app)
        self.endpoint = ui_endpoint or "administration"
        self.url = url or "/administration"
        self.base_template = base_template or "invenio_administration/base.html"

        self.create_blueprint()

        if self.dashboard_view_class is not None:
            self._add_dashboard_view()

        @app.before_first_request
        def init_menu():
            self._menu.register_menu_entries(current_menu, self._menu_key)
            self._menu.register_admin_entry(current_menu, self.endpoint)

    def load_admin_dashboard(self, app):
        """Load dashboard view configuration."""
        dashboard_config = app.config["ADMINISTRATION_DASHBOARD_VIEW"]
        dashboard_class = import_string(dashboard_config)
        return dashboard_class

    def create_blueprint(self):
        """Create Flask blueprint."""
        # Create blueprint and register rules
        self.blueprint = Blueprint(
            self.endpoint,
            __name__,
            url_prefix=self.url,
            template_folder="templates",
            static_folder="static",
        )

    @property
    def views(self):
        """Registered admin views."""
        return self._views

    def add_view(self, view, view_instance, *args, **kwargs):
        """Add a view to admin views."""
        # Validate view's class and name's uniqueness.
        if not issubclass(view.view_class, AdminView):
            raise TypeError(f"View class must be of type {AdminView.__name__}")
        if any(v.view_class.name == view.view_class.name for v in self.views):
            raise ValueError(f"View name already registered: {view.view_class.name}")

        self.views.append(view)

        self.blueprint.add_url_rule(
            rule=view_instance.url,
            view_func=view,
        )

        from invenio_administration.views.base import (
            AdminFormView,
            AdminResourceDetailView,
        )

        # TODO change to be configurable
        if not isinstance(view_instance, AdminResourceDetailView) and not isinstance(
            view_instance, AdminFormView
        ):
            self._menu.add_view_to_menu(view_instance)

    def _add_dashboard_view(self):
        """Add the admin dashboard view."""
        dashboard_instance = self.dashboard_view_class(
            admin=self, extension_name="invenio-administration"
        )
        dashboard_view = self.dashboard_view_class.as_view(
            self.dashboard_view_class.name,
            admin=self,
            extension_name="invenio-administration",
        )

        self.add_view(dashboard_view, dashboard_instance)
