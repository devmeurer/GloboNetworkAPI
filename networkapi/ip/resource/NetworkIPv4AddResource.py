# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import NetworkIPv4, NetworkIPv4AddressNotAvailableError,\
    IpNotAvailableError
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import TipoRede, NetworkTypeNotFoundError, VlanNotFoundError
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.ambiente.models import EnvironmentVip, ConfigEnvironmentInvalidError
from networkapi.vlan.models import Vlan
from networkapi.ip.models import Ip, IpEquipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.infrastructure.ip_subnet_utils import get_prefix_IPV4,\
    MAX_IPV4_HOSTS
from networkapi.config.models import Configuration


class NetworkIPv4AddResource(RestResource):

    log = Log('NetworkIPv4AddResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''
            Treat requests POST to add a network IPv4
            URL: network/ipv4/add/
        '''

        # # Commons Validations

        # User permission
        if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
            self.log.error(u'User does not have permission to perform the operation.')
            return self.not_authorized()

        # # Business Validations

        # Load XML data
        xml_map, _ = loads(request.raw_post_data)

        # XML data format
        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            msg = u'There is no value to the networkapi tag of XML request.'
            self.log.error(msg)
            return self.response_error(3, msg)
        vlan_map = networkapi_map.get('vlan')
        if vlan_map is None:
            msg = u'There is no value to the vlan tag of XML request.'
            self.log.error(msg)
            return self.response_error(3, msg)

        # Get XML data
        vlan_id = vlan_map.get('id_vlan')
        network_type = vlan_map.get('id_tipo_rede')
        environment_vip = vlan_map.get('id_ambiente_vip')
        prefix = vlan_map.get('prefix')

        # Valid prefix
        if not is_valid_int_greater_zero_param(prefix, False) or (prefix and int(prefix) > 32):
                self.log.error(u'Parameter prefix is invalid. Value: %s.', prefix)
                return self.response_error(269, 'prefix', prefix)

        return self.network_ipv4_add(user, vlan_id, network_type, environment_vip, prefix)

    def handle_put(self, request, user, *args, **kwargs):
        '''
            Treat requests PUT to add a network IPv4 with num hosts param
            URL: network/ipv4/add/
        '''

        # # Commons Validations

        # User permission
        if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
            self.log.error(u'User does not have permission to perform the operation.')
            return self.not_authorized()

        # # Business Validations

        # Load XML data
        xml_map, _ = loads(request.raw_post_data)

        # XML data format
        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            msg = u'There is no value to the networkapi tag of XML request.'
            self.log.error(msg)
            return self.response_error(3, msg)
        vlan_map = networkapi_map.get('vlan')
        if vlan_map is None:
            msg = u'There is no value to the vlan tag of XML request.'
            self.log.error(msg)
            return self.response_error(3, msg)

        # Get XML data
        vlan_id = vlan_map.get('id_vlan')
        network_type = vlan_map.get('id_tipo_rede')
        environment_vip = vlan_map.get('id_ambiente_vip')
        num_hosts = vlan_map.get('num_hosts')

        # Valid num_hosts
        if not is_valid_int_greater_zero_param(num_hosts) or int(num_hosts) > MAX_IPV4_HOSTS:
            self.log.error(u'Parameter num_hosts is invalid. Value: %s.', num_hosts)
            return self.response_error(269, 'num_hosts', num_hosts)

        num_hosts = int(num_hosts)
        # Get configuration
        conf = Configuration.get()

        num_hosts += conf.IPv4_MIN + conf.IPv4_MAX
        prefix = get_prefix_IPV4(num_hosts)
        self.log.info(u'Prefix for %s hosts: %s' % (num_hosts, prefix))

        return self.network_ipv4_add(user, vlan_id, network_type, environment_vip, prefix)

    def network_ipv4_add(self, user, vlan_id, network_type, environment_vip, prefix=None):

        try:

            # Valid vlan ID
            if not is_valid_int_greater_zero_param(vlan_id):
                self.log.error(u'Parameter id_vlan is invalid. Value: %s.', vlan_id)
                raise InvalidValueError(None, 'id_vlan', vlan_id)

            # # Network Type

            # Valid network_type ID
            if not is_valid_int_greater_zero_param(network_type):
                self.log.error(u'Parameter id_tipo_rede is invalid. Value: %s.', network_type)
                raise InvalidValueError(None, 'id_tipo_rede', network_type)

            # Find network_type by ID to check if it exist
            net = TipoRede.get_by_pk(network_type)

            # # Environment Vip

            if environment_vip is not None:

                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(environment_vip):
                    self.log.error(u'Parameter id_ambiente_vip is invalid. Value: %s.', environment_vip)
                    raise InvalidValueError(None, 'id_ambiente_vip', environment_vip)

                # Find Environment VIP by ID to check if it exist
                evip = EnvironmentVip.get_by_pk(environment_vip)

            else:
                evip = None

            # # Business Rules

            # New NetworkIPv4
            network_ipv4 = NetworkIPv4()
            vlan_map = network_ipv4.add_network_ipv4(user, vlan_id, net, evip, prefix)

            list_equip_routers_ambient = EquipamentoAmbiente.objects.filter(ambiente=network_ipv4.vlan.ambiente.id, is_router=True)

            if list_equip_routers_ambient:

                # Add Adds the first available ipv4 on all equipment
                # that is configured as a router for the environment related to network
                ip = Ip.get_first_available_ip(network_ipv4.id)

                ip = str(ip).split('.')

                ip_model = Ip()
                ip_model.oct1 = ip[0]
                ip_model.oct2 = ip[1]
                ip_model.oct3 = ip[2]
                ip_model.oct4 = ip[3]
                ip_model.networkipv4_id = network_ipv4.id

                ip_model.save(user)

                for equip in list_equip_routers_ambient:

                    IpEquipamento().create(user, ip_model.id, equip.equipamento.id)

            # Return XML
            return self.response(dumps_networkapi(vlan_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkTypeNotFoundError, e:
            self.log.error(u'The network_type parameter does not exist.')
            return self.response_error(111)
        except VlanNotFoundError, e:
            self.log.error(u'Vlan not found')
            return self.response_error(116)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except GrupoError, e:
            return self.response_error(1)
        except NetworkTypeNotFoundError, e:
            return self.response_error(111)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except NetworkIPv4AddressNotAvailableError:
            return self.response_error(295)
        except ConfigEnvironmentInvalidError:
            return self.response_error(294)
        except NetworkIPv4AddressNotAvailableError, e:
            return self.response_error(294)
        except IpNotAvailableError, e:
            return self.response_error(150, e)