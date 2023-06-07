# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class RouteMapEntryPostSuccessTestCase(NetworkApiTestCase):

    route_map_entry_uri = '/api/v4/route-map-entry/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map_entry/{}'

    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_list_config_bgp.json'),

    ]

    json_path = 'api_route_map/v4/tests/route_map_entry/sanity/json/post/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['action', 'action_reconfig', 'order', 'list_config_bgp',
                       'route_map']

    def tearDown(self):
        pass

    def test_post_route_map_entries(self):
        """Test POST RouteMapEntries."""

        route_map_entries_path = self.json_path.\
            format('two_route_map_entries.json')

        response = self.client.post(
            self.route_map_entry_uri,
            data=self.load_json(route_map_entries_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.route_map_entry_uri,
                        get_ids,
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(route_map_entries_path,
                          response.data)


class RouteMapEntryPostErrorTestCase(NetworkApiTestCase):

    route_map_entry_uri = '/api/v4/route-map-entry/'
    fixtures_path = 'networkapi/api_route_map/v4/fixtures/route_map_entry/{}'

    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_list_config_bgp.json'),
        fixtures_path.format('initial_route_map_entry.json'),
        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_vlan.json'),
        fixtures_path.format('initial_networkipv4.json'),
        fixtures_path.format('initial_ipv4.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_neighbor_v4.json'),
    ]

    json_path = 'api_route_map/v4/tests/route_map_entry/sanity/json/post/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'

    def tearDown(self):
        pass

    def test_post_route_map_entry_with_duplicated_list_config_bgp(self):
        """Test POST RouteMapEntry with duplicated ListConfigBGP."""

        route_map_entries_path = self.json_path.\
            format('duplicated_route_map_entry.json')

        response = self.client.post(
            self.route_map_entry_uri,
            data=self.load_json(route_map_entries_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            'It already exists RouteMapEntry with ListConfigBGP '
            'id = 2',
            response.data['detail']
        )

    def test_post_route_map_entry_with_deployed_route_map(self):
        """Test POST RouteMapEntry with deployed RouteMap."""

        route_map_entries_path = self.json_path.\
            format('route_map_entry_with_deployed_route_map.json')

        response = self.client.post(
            self.route_map_entry_uri,
            data=self.load_json(route_map_entries_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            'RouteMap id = 2 is deployed at '
            'NeighborsV4 = [1] and NeighborsV6 = []',
            response.data['detail']
        )
