# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission

from networkapi.rest import RestResource, UserNotAuthorizedError

from networkapi.ambiente.models import EnvironmentVip

from networkapi.requisicaovips.models import RequisicaoVips

from networkapi.auth import has_perm

from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.log import Log

from networkapi.util import is_valid_int_greater_zero_param

from networkapi.exception import InvalidValueError, EnvironmentVipError, EnvironmentVipNotFoundError

class RequestAllVipsEnviromentVipResource(RestResource):

    log = Log('RequestAllVipsEnviromentVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the VIPs related to Environment VIP. 

        URL: environmentvip/<id_environment_vip>/vip/all'
        """

        try:

            self.log.info("GET to list all the VIPs related to Environment VIP")

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Get data
            id_environment_vip = kwargs.get('id_environment_vip')

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(id_environment_vip):
                self.log.error(u'The id_environment_vip parameter is not a valid value: %s.', id_environment_vip)
                raise InvalidValueError(None, 'id_environment_vip', id_environment_vip)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(id_environment_vip)

            # Find Request VIP - IPv4 by ID Environment
            vips_ipv4 = RequisicaoVips.objects.filter(ip__networkipv4__ambient_vip__id = environment_vip.id)

            # Find Request VIP - IPv6 by ID Environment
            vips_ipv6 = RequisicaoVips.objects.filter(ipv6__networkipv6__ambient_vip__id = environment_vip.id)

            vips = {}
            for vips_ip in [vips_ipv4, vips_ipv6]:

                for vip in vips_ip:

                    v = {}
                    v = vip.variables_to_map()
                    v['id'] = vip.id
                    v['validado'] = vip.validado
                    v['vip_criado'] = vip.vip_criado
                    v['id_ip'] = vip.ip_id
                    v['id_ipv6'] = vip.ipv6_id
                    v['id_healthcheck_expect'] = vip.healthcheck_expect_id
                    vips['vip_%s' % (vip.id)] = v

            return self.response(dumps_networkapi(vips))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except EnvironmentVipError:
            return self.response_error(1)