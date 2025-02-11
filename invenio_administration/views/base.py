# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Administration views base module."""
import requests
import json
from sickle import Sickle
from functools import partial
import os
from ratelimit import limits, sleep_and_retry
from datetime import datetime
import time
from bs4 import BeautifulSoup
from .translate import *
from .project import *
from .publish import *
from .model import *

from flask import current_app, render_template, url_for
from flask.views import MethodView
from invenio_search_ui.searchconfig import search_app_config
from invenio_banners.records.models import BannerModel

from invenio_administration.errors import (
    InvalidActionsConfiguration,
    InvalidExtensionName,
    InvalidResource,
    MissingDefaultGetView,
    MissingExtensionName,
    MissingResourceConfiguration,
)
from invenio_administration.marshmallow_utils import jsonify_schema
from invenio_administration.permissions import administration_permission

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import JSON
Base = declarative_base()



class AdminView(MethodView):
    """Base view for admin views."""

    extension_name = None
    name = None
    category = None
    template = "invenio_administration/index.html"
    url = None
    menu_label = None
    order = None
    icon = None

    decorators = [administration_permission.require(http_exception=403)]

    def __init__(
        self,
        name=__name__,
        category=None,
        url=None,
        extension_name=None,
        admin=None,
        order=0,
        icon=None,
    ):
        """Constructor."""
        if self.extension_name is None:
            self.extension_name = extension_name

        if self.name is None:
            self.name = name

        if self.category is None:
            self.category = category

        if self.menu_label is None:
            self.menu_label = self.name

        self.administration = admin

        if self.order is None:
            self.order = order

        if self.icon is None:
            self.icon = icon

        self.url = url or self._get_view_url(self.url)

        # Default view
        if self.get is None:
            raise MissingDefaultGetView(self.__class__.__name__)

    @staticmethod
    def disabled():
        """Determine if the view should be disabled."""
        return False

    @property
    def endpoint(self):
        """Get name for endpoint location e.g: 'administration.index'."""
        if self.administration is None:
            return self.name
        return f"{self.administration.endpoint}.{self.name}"

    @classmethod
    def _get_view_extension(cls, extension_name=None):
        """Get the flask extension of the view."""
        try:
            if extension_name:
                return current_app.extensions[extension_name]
            return current_app.extensions[cls.extension_name]
        except KeyError:
            raise InvalidExtensionName(extension_name)

    def _get_view_url(self, url):
        """Generate URL for the view. Override to change default behavior."""
        new_url = url
        if new_url is None:
            if isinstance(self, self.administration.dashboard_view_class):
                new_url = "/"
            else:
                new_url = "/%s" % self.name.lower()
        else:
            if not url.startswith("/"):
                new_url = "/%s" % (url)
        # Sanitize url
        new_url = new_url.replace(" ", "_")
        return new_url

    def _get_template(self):
        return self.template

    def render(self, **kwargs):
        """Render template."""
        kwargs["admin_base_template"] = self.administration.base_template
        return render_template(self._get_template(), **kwargs)

    def get(self):
        """GET view method."""
        return self.render()


class AdminResourceBaseView(AdminView):
    """Base view for admin resources."""

    display_edit = False
    display_delete = False
    resource_config = None
    resource = None
    actions = {}
    schema = None
    api_endpoint = None
    pid_path = "pid"
    title = None
    resource_name = None

    create_view_name = None
    list_view_name = None
    request_headers = {"Accept": "application/json"}

    def __init__(
        self,
        name=__name__,
        category=None,
        url=None,
        extension_name=None,
        admin=None,
        order=0,
        icon=None,
    ):
        """Constructor."""
        super().__init__(name, category, url, extension_name, admin, order, icon)

        if self.extension_name is None:
            raise MissingExtensionName(self.__class__.__name__)
        if self.resource_config is None:
            raise MissingResourceConfiguration(self.__class__.__name__)

    @classmethod
    def set_schema(cls):
        """Set schema."""
        cls.schema = cls.get_service_schema()

    @classmethod
    def set_resource(cls, extension_name=None):
        """Set resource."""
        cls.resource = cls._get_resource(extension_name)

    @classmethod
    def _get_resource(cls, extension_name=None):
        extension_name = cls._get_view_extension(extension_name)
        try:
            return getattr(extension_name, cls.resource_config)
        except AttributeError:
            raise InvalidResource(resource=cls.resource_config, view=cls.__name__)

    @classmethod
    def get_service_schema(cls):
        """Get marshmallow schema of the assigned service."""
        # schema.schema due to the schema wrapper imposed,
        # when the actual class needed
        return cls.resource.service.schema.schema()

    def _schema_to_json(self, schema):
        """Translate marshmallow schema to JSON.

        Provides action payload template for the frontend.
        """
        return jsonify_schema(schema)

    def get_api_endpoint(self):
        """Get search API endpoint."""
        api_url_prefix = current_app.config["SITE_API_URL"]
        slash_tpl = "/" if not self.api_endpoint.startswith("/") else ""

        if not self.api_endpoint.startswith(api_url_prefix):
            return f"{api_url_prefix}{slash_tpl}{self.api_endpoint}"

        return f"{slash_tpl}{self.api_endpoint}"

    def serialize_actions(self):
        """Serialize actions for the resource frontend view.

        {"action_name":
            {"text": "Action"
             "payload_schema": schema in json
             "order": 1
             }
         }
        """
        serialized_actions = {}
        for key, value in self.actions.items():
            if "payload_schema" and "order" not in value:
                raise InvalidActionsConfiguration

            serialized_actions[key] = {"text": value["text"], "order": value["order"]}
            if value["payload_schema"] is not None:
                serialized_actions[key]["payload_schema"] = self._schema_to_json(
                    value["payload_schema"]()
                )

        return serialized_actions

    def get_list_view_endpoint(self):
        """Returns administration UI list view endpoint."""
        if self.list_view_name:
            return url_for(f"administration.{self.list_view_name}")
        if isinstance(self, AdminResourceListView):
            return url_for(f"administration.{self.name}")

    def get_create_view_endpoint(self):
        """Returns administration UI list view endpoint."""
  
        if self.create_view_name:
            return url_for(f"administration.{self.create_view_name}")


class AdminResourceDetailView(AdminResourceBaseView):
    """Details view based on given config."""

    display_edit = True
    display_delete = True

    name = None
    item_field_exclude_list = None
    item_field_list = None
    template = "invenio_administration/details.html"
    title = "Resource details"

    def get_context(self, pid_value=None):
        """Create details view context."""
        name = self.name
        schema = self.get_service_schema()
        serialized_schema = self._schema_to_json(schema)
        fields = self.item_field_list
        return {
            "request_headers": self.request_headers,
            "name": name,
            "resource_schema": serialized_schema,
            "fields": fields,
            "exclude_fields": self.item_field_exclude_list,
            "ui_config": self.item_field_list,
            "pid": pid_value,
            "api_endpoint": self.get_api_endpoint(),
            "title": self.title,
            "list_endpoint": self.get_list_view_endpoint(),
            "actions": self.serialize_actions(),
            "pid_path": self.pid_path,
            "display_edit": self.display_edit,
            "display_delete": self.display_delete,
            "list_ui_endpoint": self.get_list_view_endpoint(),
            "resource_name": self.resource_name
            if self.resource_name
            else self.pid_path,
            "request_headers": self.request_headers,
        }

    def get(self, pid_value=None):
        """GET view method."""
        return self.render(**self.get_context(pid_value=pid_value))



class AdminFormView(AdminResourceBaseView):
    """Basic form view."""

    form_fields = None
    display_read_only = True

    """Basic form view."""
    host = "localhost"
    user = "root"
    password = ""
    database = "file_storage"

    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()


    def get(self, pid_value=None):
        check_api_endpoint = self.api_endpoint
        if check_api_endpoint == "/pages":
            project_function()
            translate_function()
            publish_function()
        """GET view method."""
        oaiurl = ""
        for record in BannerModel.query.filter_by(id=pid_value):
            oaiurl = record.oai_url
            oaiset = record.set_name
            reponame = record.repo_name


        if self.url == "/banners/<pid_value>/edit":
            api = "https://127.0.0.1:5000"
            token = "m1VuHtbNzvxjZuLfBs8PeIVsnAEETt31K2gnmPwKVQxZyOi7BZruP1iO0klT"
            sickle = Sickle(oaiurl)
            if(oaiset==''):
                records = sickle.ListRecords(metadataPrefix='oai_dc', ignore_deleted=True)
            else:
                records = sickle.ListRecords(metadataPrefix='oai_dc', set=oaiset, ignore_deleted=True)
            @sleep_and_retry
            @limits(calls=1, period=10) # 1 request per second
            def make_api_request(req_url):
                response = requests.get(req_url)
                return response
            for record in records:
                meta = record.metadata
                creators_list=[]
                try:
                    for author in meta['creator']:
                        creators_list.append(
                            {
                                "person_or_org":{
                                    "family_name": author,
                                    "type": "personal"                                                                        
                                }
                            }                            
                        )
                except:
                    creators_list.append(
                            {
                                "person_or_org":{
                                    "family_name": 'N/A',
                                    "type": "personal"                                                                        
                                }
                            }                            
                        )
                try:    
                    date_string = meta['date'][0]
                    date_format = "%Y-%m-%dT%H:%M:%SZ"
                    input_date = datetime.strptime(date_string, date_format)
                    publdate = input_date.strftime("%Y-%m-%d")
                except:
                    publdate = meta['date'][0]
                
                contributors_list=[]
                try:
                    for contributor_item in meta['contributor']:
                        contributors_list.append(
                            {
                                "person_or_org":{
                                    "type": "personal",
                                    "name": contributor_item,
                                    "family_name": contributor_item
                                },
                                "role": {
                                    "id": "other"
                                }
                            }
                        )    
                except:
                    contributors_list=[]                                   
                
                description = meta.get('description',[''])[0]
                
                try:
                    identifier_list = meta['identifier']
                    identifier=""
                    for identify in identifier_list:
                        if identify.startswith('http'):
                            identifier=identify
                            break
                except:
                    identifier=''

                rectitle = meta.get('title',['N/A'])[0]

                try:
                    rights = meta['rights']
                    rights_title = rights[0]
                    rights_link=""
                    for right in rights:
                        if right.startswith('http'):
                            rights_link=right
                            break
                except:
                    rights_title = ''
                    rights_link = ''

                subjects_list=[]
                try:
                    for subject in meta['subject']:
                        subjects_list.append(
                            {
                                "subject": subject
                            }
                        )
                except:
                    subjects_list.append(
                        {
                            "subject": ''
                        }
                    )

                publisher = meta.get('publisher',[reponame])[0]

                restype = 'other'

                datameta = {
                    "access": {
                        "files": "public",
                        "record": "public"
                    },
                    "files": {
                        "enabled": True
                    },
                    "metadata": {
                        "creators": creators_list,
                        "description": description,
                        "identifiers": [{
                        "identifier": identifier,
                        "scheme": "other"
                        }],
                        "publication_date": publdate,
                        "publisher": publisher,
                        "contributors": contributors_list,
                        "resource_type": {
                        "id": restype
                        },
                        "rights": [
                        {
                            "title": {
                            "en": rights_title
                            },
                            "link": rights_link
                        }
                        ],
                        "subjects": subjects_list,
                        "title": rectitle,
                        "version": "v1"
                    },
                    "custom_fields": {
                        "invisible_search": ""
                    },
                    "pids": {}
                    }

                h = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                    }
                fh = {
                    "Accept": "application/json",
                    "Content-Type": "application/octet-stream",
                    "Authorization": f"Bearer {token}"
                    }

                title=meta['title'][0]
                title_split=title.split(" ")
                title_concat=title_split[0]
                id_list=meta['identifier']
                for iden in id_list:
                    if iden.startswith('http'):
                        rec_url=iden
                        break
                rec_url_split=rec_url.split('/')[-1]
                file_name_short=title_concat+rec_url_split
                output_directory='.'
                rec_response = make_api_request(rec_url)
                rec_path = os.path.join(output_directory, f"rec_{title}.html")
                
                with open(rec_path, "wb") as file:
                    file.write(rec_response.content)
                
                with open(rec_path, 'r') as file:
                    html = file.read()
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    element = soup.find('meta', {'name': 'citation_pdf_url'})
                except:
                    continue
                time.sleep(5)
                try:
                    file_url=element['content']
                except:
                    continue
                file_response = make_api_request(file_url)
                content_type = file_response.headers.get("Content-Type")
                slash = content_type.split('/')
                extension = slash[-1].split(';')[0]

                file_path = os.path.join(output_directory, f"{file_name_short}.{extension}")

                with open(file_path, "wb") as file:
                    file.write(file_response.content)
                new_file = OriginalFile(file_name=file_name_short, file_data=file_response.content, file_type=extension,metadata_file=datameta)
                self.session.add(new_file)
                self.session.commit()
                self.session.close()
    
        
        schema = self.get_service_schema()
        serialized_schema = self._schema_to_json(schema)
        form_fields = self.form_fields
        return self.render(
            **{
                "resource_schema": serialized_schema,
                "form_fields": form_fields,
                "pid": pid_value,
                "api_endpoint": self.get_api_endpoint(),
                "title": self.title,
                "list_endpoint": self.get_list_view_endpoint(),
                "ui_config": self.form_fields,
            }
        )


class AdminResourceEditView(AdminFormView):
    """Admin resource edit view."""

    template = "invenio_administration/edit.html"
    title = "Edit resource"


class AdminResourceCreateView(AdminFormView):
    """Admin resource edit view."""

    template = "invenio_administration/create.html"
    title = "Create resource"


class AdminResourceListView(AdminResourceBaseView):
    """List view based on provided resource."""

    template = "invenio_administration/search.html"

    # decides if there is a detail view
    display_read = True
    display_create = True
    display_translate = True
    
    # hides searchbar
    display_search = True

    search_config_name = None
    search_facets_config_name = None
    search_sort_config_name = None
    sort_options = {}
    available_facets = {}
    item_field_exclude_list = None
    item_field_list = None
    api_endpoint = None
    item_api_endpoint = None
    title = None

    search_request_headers = {"Accept": "application/json"}

    def get_search_request_headers(self):
        """Get search request headers."""
        # print("THIS IS EDIT 19")
        return self.search_request_headers

    def get_search_app_name(self):
        """Get search app name."""
        # print("THIS IS EDIT 20")
        if self.search_config_name is None:
            return f"{self.name.upper()}_SEARCH"
        return self.search_config_name

    def init_search_config(self):
        """Build search view config."""
        # print("THIS IS EDIT 21")
        return partial(
            search_app_config,
            config_name=self.get_search_app_name(),
            available_facets=current_app.config.get(self.search_facets_config_name),
            sort_options=current_app.config[self.search_sort_config_name],
            endpoint=self.get_api_endpoint(),
            headers=self.get_search_request_headers(),
        )

    def get_sort_options(self):
        """Get search sort options."""
        # print("THIS IS EDIT 22")
        if not self.sort_options:
            return self.resource.service.config.search.sort_options
        return self.sort_options

    def get_available_facets(self):
        """Get search available facets."""
        # print("THIS IS EDIT 23")
        if not self.available_facets:
            return self.resource.service.config.search.facets
        return self.available_facets

    def get(self):
        """GET view method."""
        # print("THIS IS EDIT 24")
        search_conf = self.init_search_config()
        schema = self.get_service_schema()
        serialized_schema = self._schema_to_json(schema)
        return self.render(
            **{
                "search_config": search_conf,
                "api_endpoint": self.get_api_endpoint(),
                "title": self.title,
                "name": self.name,
                "resource_schema": serialized_schema,
                "fields": self.item_field_list,
                "display_search": self.display_search,
                "display_create": self.display_create,
                "display_translate": self.display_translate,
                "display_edit": self.display_edit,
                "display_delete": self.display_delete,
                "display_read": self.display_read,
                "actions": self.serialize_actions(),
                "pid_path": self.pid_path,
                "create_ui_endpoint": self.get_create_view_endpoint(),
                "list_ui_endpoint": self.get_list_view_endpoint(),
                "resource_name": self.resource_name
                if self.resource_name
                else self.pid_path,
            }
        )


class AdminResourceViewSet:
    """View set based on resource.

    Provides a list view and a details view given the provided configuration.
    """

    extension_name = None
    name = None
    category = None
    template = "invenio_administration/index.html"
    url = None
    menu_label = None

    resource_config = None
    resource = None

    schema = None
    api_endpoint = None
    pid_path = "pid"
    title = None
    actions = None

    create_view_name = None
    edit_view_name = None
    details_view_name = None
    list_view_name = None

    display_create = False
    display_read = True
    display_edit = False
    display_delete = False
    display_translate = False
    
    sort_options = ()
    available_filters = None
    item_field_exclude_list = None
    item_field_list = None

    def list_view(self):
        """List view."""
        # print("THIS IS EDIT 25")
        pass

    def details_view(self):
        """Details view."""
        # print("THIS IS EDIT 26")
        pass

    def edit_view(self):
        """Details view."""
        # print("THIS IS EDIT 27")
        pass

    def create_view(self):
        """Details view."""
        # print("THIS IS EDIT 28")
        pass
