# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class ListConfigBGPDeleteSuccessTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_list_config_bgp.json'),

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_lists_config_bgp(self):
        """Test DELETE ListsConfigBGP."""

        delete_ids = [1]
        uri = mount_url(self.list_config_bgp_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)
        self.compare_values(
            'ListConfigBGP id = 1 do not exist',
            response.data['detail']
        )


class ListConfigBGPDeleteErrorTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_list_config_bgp.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_route_map_entry.json'),

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_list_config_bgp_assoc_to_route_map_entry(self):
        """Test DELETE ListConfigBGP associated to RouteMapEntry."""

        delete_ids = [1]
        uri = mount_url(self.list_config_bgp_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)

        self.compare_values(
            'ListConfigBGP id = 1 is associated '
            'in RouteMapEntries = [1]',
            response.data['detail']
        )

    def test_delete_inexistent_lists_config_bgp(self):
        """Test DELETE inexistent ListsConfigBGP."""

        delete_ids = [1000, 1001]
        uri = mount_url(self.list_config_bgp_uri,
                        delete_ids)

        response = self.client.delete(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            'ListConfigBGP id = 1000 do not exist',
            response.data['detail']
        )
