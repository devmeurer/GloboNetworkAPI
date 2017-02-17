# -*- coding: utf-8 -*-
import json
import logging

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


def setup():
    call_command(
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        verbosity=0
    )


class EnvironmentGetTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """Test of success for get one environment."""

        response = self.client.get(
            '/api/v3/environment/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_success_two_environments(self):
        """Test of success for get two environment."""

        response = self.client.get(
            '/api/v3/environment/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_success_list_environments(self):
        """Test of success of the list of environments."""

        response = self.client.get(
            '/api/v3/environment/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_success_one_environment_with_details(self):
        """Test Success of get one environment with details."""
        name_file = 'api_environment/tests/sanity/json/get_one_env_details.json'

        response = self.client.get(
            '/api/v3/environment/1/?kind=details',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_success_one_environment_with_routers(self):
        """Test Success of get one environment with routers."""

        response = self.client.get(
            '/api/v3/environment/1/?include=routers',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data['environments'][0]['routers']
        expected_data = [
            {'id': 1L},
            {'id': 2L}
        ]
        self.assertEqual(
            expected_data,
            data,
            'Routers should be %s and was %s' % (expected_data, data)
        )

    def test_get_success_one_environment_with_equipments(self):
        """Test Success of get one environment with equipments."""

        response = self.client.get(
            '/api/v3/environment/1/?include=equipments',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data['environments'][0]['equipments']

        expected_data = [
            {'id': 1},
            {'id': 2},
            {'id': 7},
            {'id': 8}
        ]

        expected_data.sort()

        data.sort()

        self.assertEqual(
            json.dumps(expected_data, sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Equipments should be %s and was %s' % (expected_data, data)
        )

    def test_get_success_one_environment_with_children(self):
        """Test Success of get one environment with children."""

        response = self.client.get(
            '/api/v3/environment/4/?include=children',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data['environments'][0]['children']

        expected_data = [
            {'id': 1L, 'name': u'BE - SANITY-TEST-1 - RACK-1', 'children': []},
            {'id': 2L, 'name': u'BE - SANITY-TEST-1 - RACK-2', 'children': []}
        ]

        self.assertEqual(
            json.dumps(expected_data, sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Children should be %s and was %s' % (expected_data, data)
        )

    def test_get_success_list_envs_rel_envvip(self):
        """Test of success of the list of environments related with
        environments vip.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_success_list_envs_by_envvip(self):
        """Test of success of the list of environments by environment vip id.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_error_one_environment(self):
        """Test of error for get one environment."""

        response = self.client.get(
            '/api/v3/environment/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

    def test_get_error_list_envs_by_envvip(self):
        """Test of error of the list of environments by nonexistent id of the
        vip environment.
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)
