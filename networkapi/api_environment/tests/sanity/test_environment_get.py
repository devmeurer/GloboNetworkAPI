# -*- coding: utf-8 -*-
import json
import logging

from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentGetOneSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    json_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """Test of success to get one environment."""

        response = self.client.get(
            '/api/v3/environment/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_one_environment_with_details(self):
        """Test of success to get one environment with details."""

        name_file = self.json_path % 'get_one_env_details.json'

        response = self.client.get(
            '/api/v3/environment/1/?kind=details',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_success_one_environment_with_routers(self):
        """Test of success to get one environment with routers."""

        response = self.client.get(
            '/api/v3/environment/1/?include=routers',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        data = json.dumps(response.data['environments'][0]['routers'],
                          sort_keys=True)
        expected_data = [
            {'id': 1L},
            {'id': 2L}
        ]
        expected_data = json.dumps(expected_data, sort_keys=True)

        self.compare_values(expected_data, data)

    def test_get_success_one_environment_with_equipments(self):
        """Test of success to get one environment with equipments."""

        response = self.client.get(
            '/api/v3/environment/1/?include=equipments',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        data = json.dumps(response.data['environments'][0]['equipments'],
                          sort_keys=True)
        expected_data = [
            {'id': 1},
            {'id': 2},
            {'id': 7},
            {'id': 8}
        ]
        expected_data = json.dumps(expected_data, sort_keys=True)
        self.compare_values(expected_data, data)

    def test_get_success_one_environment_with_equipments_and_controllers(self):
        """
        Test of success to get one environment with equipments and SDN
        controllers
        """

        response = self.client.get(
            '/api/v3/environment/1/?include=equipments,sdn_controllers',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        data = json.dumps(response.data['environments'][0]['equipments'],
                          sort_keys=True)
        expected_data = [
            {'id': 1},
            {'id': 2},
            {'id': 7},
            {'id': 8}
        ]

        expected_data = json.dumps(expected_data, sort_keys=True)
        self.compare_values(expected_data, data)
        assert isinstance(response.data["environments"][0]["sdn_controllers"],
                          list), "Wrong controller data type. Must be a list"
        assert len(response.data["environments"][0]["sdn_controllers"]) > 0, \
            "sdn_controllers must have at least one entry"

    def test_get_success_one_environment_with_children(self):
        """Test of success to get one environment with children."""

        response = self.client.get(
            '/api/v3/environment/4/?include=children',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        data = json.dumps(response.data['environments'][0]['children'],
                          sort_keys=True)

        expected_data = [
            {'id': 1L, 'name': 'BE - SANITY-TEST-1 - RACK-1', 'children': []},
            {'id': 2L, 'name': 'BE - SANITY-TEST-1 - RACK-2', 'children': []}
        ]

        expected_data = json.dumps(expected_data, sort_keys=True)

        self.compare_values(expected_data, data)


class EnvironmentGetTwoSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
    ]

    json_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_get_success_two_environments(self):
        """Test of success to get two environment."""

        name_file = self.json_path % 'get_two_env.json'

        response = self.client.get(
            '/api/v3/environment/1;2/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)


class EnvironmentGetListSuccessTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
    ]

    json_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_get_success_list_environments(self):
        """Test of success of the list of environments."""

        response = self.client.get(
            '/api/v3/environment/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_list_envs_rel_envvip(self):
        """Test of success of the list of environments related with
        environments vip.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_get_success_list_envs_by_envvip(self):
        """Test of success of the list of environments by environment vip id.
        """

        name_file = self.json_path % 'get_list_envs_by_envvip.json'

        response = self.client.get(
            '/api/v3/environment/environment-vip/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)


class EnvironmentGetErrorTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_get_error_one_environment(self):
        """Test of error to get one environment."""

        response = self.client.get(
            '/api/v3/environment/1000/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Causa: , Mensagem: There is no environment with id = 1000.',
            response.data['detail'])

    def test_get_error_list_envs_by_envvip(self):
        """Test of error of the list of environments by nonexistent id of the
        vip environment.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/1000/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Cause: , Message: There is no environment vip by pk = 1000.',
            response.data['detail'])
