# -*- coding: utf-8 -*-
import logging

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class IPv4DeleteTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/api_pools/fixtures/initial_optionspool.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/healthcheckexpect/fixtures/initial_healthcheck.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/fixtures/initial_base.json',
        'networkapi/api_ip/fixtures/initial_base_v4.json',
        'networkapi/api_ip/fixtures/initial_pool.json',
        'networkapi/api_ip/fixtures/initial_vip_request_v4.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    # DELETE functional tests

    def test_try_delete_existent_ipv4(self):
        """Tests if NAPI can delete a existent IPv4 Address."""

        response = self.client.delete(
            '/api/v3/ipv4/1/')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/ipv4/1/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 1.',
            response.data['detail']
        )

    def test_try_delete_non_existent_ipv4(self):
        """Tests if NAPI returns error on deleting
        a not existing IPv4 Addresses.
        """

        response = self.client.delete(
            '/api/v3/ipv4/1000/')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 1000.',
            response.data['detail']
        )

    def test_try_delete_two_non_existent_ipv4(self):
        """Tests if NAPI returns error on deleting
        two not existing IPv4 Addresses.
        """

        response = self.client.delete(
            '/api/v3/ipv4/1000;1001/')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 1000.',
            response.data['detail']
        )

    def test_try_delete_one_existent_and_non_existent_ipv4(self):
        """Tests if NAPI deny delete at same time an existent
        and a not existent IPv4 Address.
        """

        response = self.client.delete(
            '/api/v3/ipv4/1;1001/')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 1001.',
            response.data['detail']
        )

        # Does get request
        response = self.client.get(
            '/api/v3/ipv4/1/',
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_try_delete_ipv4_assoc_to_equipment(self):
        """Tests if NAPI can delete an IPv4 Address associated to some
        equipment.
        """

        response = self.client.delete(
            '/api/v3/ipv4/2/')
        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v3/ipv4/2/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 2.',
            response.data['detail']
        )

    def test_try_delete_two_existent_ipv4(self):
        """Tests of NAPI can delete at same time
        two existent IPv4 Addresses.
        """

        response = self.client.delete(
            '/api/v3/ipv4/1;2/')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/ipv4/1;2/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 1.',
            response.data['detail']
        )

    def test_try_delete_ipv4_used_by_not_created_vip_request(self):
        """Tests if NAPI can delete an IPv4 Address used
        in a not deployed VIP Request.
        """

        response = self.client.delete(
            '/api/v3/ipv4/4/')

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/ipv4/4/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no IP with pk = 4.',
            response.data['detail']
        )

        # Does get request
        response = self.client.get(
            '/api/v3/vip-request/1/',
            content_type='application/json')

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Vip Request Does Not Exist.',
            response.data['detail']
        )

    def test_try_delete_ipv4_used_by_created_vip_request(self):
        """Tests if NAPI deny deleting of IPv4 Address used
        in deployed VIP Request.
        """
        response = self.client.delete(
            '/api/v3/ipv4/5/')

        self.compare_status(400, response.status_code)

        self.compare_values(
            'IPv4 can not be removed because it is in use'
            ' by Vip Request: 2',
            response.data['detail']
        )

        # Does get request
        response = self.client.get(
            '/api/v3/vip-request/2/',
            content_type='application/json')

        self.compare_status(200, response.status_code)
