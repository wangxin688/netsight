from sqladmin import ModelView

from src.features.org import models


class SiteGroupView(ModelView, model=models.SiteGroup):
    name = "Site Group"
    name_plural = "Site Groups"
    category = "Organization"

    column_list = [
        models.SiteGroup.id,
        models.SiteGroup.name,
        models.SiteGroup.description,
        models.SiteGroup.site_count,
        models.SiteGroup.created_at,
        models.SiteGroup.updated_at,
        models.SiteGroup.created_by,
        models.SiteGroup.updated_by,
    ]

    column_sortable_list = [models.SiteGroup.name]
    column_filters = [models.SiteGroup.name]
    page_size = 20
    page_size_options = [20, 50, 100, 200]
    form_create_rules = ["name", "description"]


class SiteView(ModelView, model=models.Site):
    name = "Site"
    name_plural = "Sites"
    category = "Organization"

    column_list = [
        models.Site.id,
        models.Site.name,
        models.Site.site_code,
        models.Site.status,
        models.Site.country,
        models.Site.city,
        models.Site.site_group,
        models.Site.network_contact,
        models.Site.it_contact,
        models.Site.created_at,
        models.Site.updated_at,
        models.Site.created_by,
        models.Site.updated_by,
    ]

    column_sortable_list = [models.Site.name, models.Site.site_code]
    column_filters = [models.Site.name]
    page_size = 20
    page_size_options = [20, 50, 100, 200]


class LocationView(ModelView, model=models.Location):
    name = "Location"
    name_plural = "Locations"
    category = "Organization"

    column_list = [
        models.Location.id,
        models.Location.name,
        models.Location.site,
        models.Location.location_type,
        models.Location.status,
        models.Location.created_at,
        models.Location.updated_at,
        models.Location.created_by,
        models.Location.updated_by,
    ]

    column_sortable_list = [models.Location.name]
    column_filters = [models.Location.name]
    page_size = 20
    page_size_options = [20, 50, 100, 200]
