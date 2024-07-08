import pytest

from src.features.org.services import site_service
from tests import factoreis


class TestSiteGroup:
    @pytest.fixture()
    async def sites(self, session):
        sites = [
            factoreis.SiteCreateFactory.build(country="China", status="Active"),
            factoreis.SiteCreateFactory.build(country="United States", status="Active"),
        ]
        db_sites = []
        for site in sites:
            new = await site_service.create(session, site)
            db_sites.append(new)
        return db_sites

    async def test_create_site_group(self, client, sites):
        new_site_group = factoreis.SiteGroupCreateFactory.build()
        new_site_group.site = []
        response = await client.post("/api/dcim/site-groups", json=new_site_group.model_dump())
        assert response.status_code == 200

        new_site_group.site = [site.id for site in sites]
        response = await client.post("/api/dcim/site-groups", json=new_site_group.model_dump())
        assert response.status_code == 200
