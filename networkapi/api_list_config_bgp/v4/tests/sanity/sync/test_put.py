# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class ListConfigBGPPutSuccessTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

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

        fixtures_path.format('initial_list_config_bgp.json'),
    ]

    json_path = 'api_list_config_bgp/v4/tests/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['id', 'name', 'type', 'config']

    def tearDown(self):
        pass

    def test_put_lists_config_bgp(self):
        """Test PUT ListsConfigBGP."""

        lists_config_bgp_path = self.json_path.\
            format('two_lists_config_bgp.json')

        response = self.client.put(
            self.list_config_bgp_uri,
            data=self.load_json(lists_config_bgp_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.list_config_bgp_uri,
                        get_ids,
                        kind=['basic'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(lists_config_bgp_path,
                          response.data)


class ListConfigBGPPutErrorTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

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

        fixtures_path.format('initial_asn.json'),
        fixtures_path.format('initial_vrf.json'),
        fixtures_path.format('initial_environment.json'),
        fixtures_path.format('initial_vlan.json'),
        fixtures_path.format('initial_networkipv4.json'),
        fixtures_path.format('initial_ipv4.json'),
        fixtures_path.format('initial_list_config_bgp.json'),
        fixtures_path.format('initial_route_map.json'),
        fixtures_path.format('initial_route_map_entry.json'),
        fixtures_path.format('initial_peer_group.json'),
        fixtures_path.format('initial_neighbor_v4.json'),

    ]

    json_path = 'api_list_config_bgp/v4/tests/sanity/json/put/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'

    def tearDown(self):
        pass

    def test_put_inexistent_list_config_bgp(self):
        """Test PUT inexistent ListConfigBGP."""

        list_config_bgp_path = self.json_path.\
            format('inexistent_list_config_bgp.json')

        response = self.client.put(
            self.list_config_bgp_uri,
            data=self.load_json(list_config_bgp_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)
        self.compare_values(
            'ListConfigBGP id = 1000 do not exist',
            response.data['detail']
        )

    def test_put_list_config_bgp_assoc_to_deployed_neighbors(self):
        """Test PUT ListConfigBGP associated to deployed Neighbors."""

        list_config_bgp_path = self.json_path.\
            format('list_config_bgp_assoc_to_deployed_neighbors.json')

        response = self.client.put(
            self.list_config_bgp_uri,
            data=self.load_json(list_config_bgp_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)
        self.compare_values(
            'ListConfigBGP id = 1 is deployed at NeighborsV4 = [1] '
            'and NeighborsV6 = []',
            response.data['detail']
        )
