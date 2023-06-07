# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import with_statement

import logging

from django.db.utils import IntegrityError

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VLAN
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpCantRemoveFromServerPool
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import mount_ipv4_string
from networkapi.util import mount_ipv6_string
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanCantDeallocate
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError


class VlanDeallocateResource(RestResource):

    log = logging.getLogger('VlanDeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to deallocate all relationships between Vlan.

        URL: vlan/<id_vlan>/deallocate/
        """

        self.log.info('Deallocate all relationships between Vlan.')

        try:

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load URL param
            id_vlan = kwargs.get('id_vlan')

            # Valid vlan id
            if not is_valid_int_greater_zero_param(id_vlan):
                self.log.error(
                    'The id_vlan parameter is not a valid value: %s.', id_vlan)
                raise InvalidValueError(None, 'id_vlan', id_vlan)

            # Find Vlan by id to check if it exist
            vlan = Vlan().get_by_pk(id_vlan)

            # Delete vlan's cache
            destroy_cache_function([id_vlan])

            # Delete equipment's cache
            equip_id_list = []

            for netv4 in vlan.networkipv4_set.all():
                for ipv4 in netv4.ip_set.all():

                    server_pool_member_list = ServerPoolMember.objects.filter(
                        ip=ipv4)

                    if server_pool_member_list.count() != 0:

                        # IP associated with Server Pool
                        server_pool_name_list = set()

                        for member in server_pool_member_list:
                            item = '{}: {}'.format(
                                member.server_pool.id, member.server_pool.identifier)
                            server_pool_name_list.add(item)

                        server_pool_name_list = list(server_pool_name_list)
                        server_pool_identifiers = ', '.join(
                            server_pool_name_list)

                        ip_formated = mount_ipv4_string(ipv4)
                        vlan_name = vlan.nome
                        network_ip = mount_ipv4_string(netv4)

                        raise IpCantRemoveFromServerPool({'ip': ip_formated, 'vlan_name': vlan_name, 'network_ip': network_ip, 'server_pool_identifiers': server_pool_identifiers},
                                                         'Não foi possível excluir a vlan %s pois ela possui a rede %s e essa rede possui o ip %s contido nela, e esse ip esta sendo usado nos Server Pools (id:identifier) %s' %
                                                         (vlan_name, network_ip, ip_formated, server_pool_identifiers))

                    for ip_equip in ipv4.ipequipamento_set.all():
                        equip_id_list.append(ip_equip.equipamento_id)

            for netv6 in vlan.networkipv6_set.all():
                for ip in netv6.ipv6_set.all():

                    server_pool_member_list = ServerPoolMember.objects.filter(
                        ipv6=ip)

                    if server_pool_member_list.count() != 0:

                        # IP associated with Server Pool
                        server_pool_name_list = set()

                        for member in server_pool_member_list:
                            item = '{}: {}'.format(
                                member.server_pool.id, member.server_pool.identifier)
                            server_pool_name_list.add(item)

                        server_pool_name_list = list(server_pool_name_list)
                        server_pool_identifiers = ', '.join(
                            server_pool_name_list)

                        ip_formated = mount_ipv6_string(ip)
                        vlan_name = vlan.nome
                        network_ip = mount_ipv6_string(netv6)

                        raise IpCantRemoveFromServerPool({'ip': ip_formated, 'vlan_name': vlan_name, 'network_ip': network_ip, 'server_pool_identifiers': server_pool_identifiers},
                                                         'Não foi possível excluir a vlan %s pois ela possui a rede %s e essa rede possui o ip %s contido nela, e esse ip esta sendo usado nos Server Pools (id:identifier) %s' %
                                                         (vlan_name, network_ip, ip_formated, server_pool_identifiers))

                    for ip_equip in ip.ipv6equipament_set.all():
                        equip_id_list.append(ip_equip.equipamento_id)

            destroy_cache_function(equip_id_list, True)

            with distributedlock(LOCK_VLAN % id_vlan):

                # Remove Vlan
                vlan.delete_v3()

                return self.response(dumps_networkapi({}))

        except IpCantRemoveFromServerPool, e:
            return self.response_error(387, e.cause.get('vlan_name'), e.cause.get('network_ip'), e.cause.get('ip'), e.cause.get('server_pool_identifiers'))
        except EquipamentoAmbienteNotFoundError as e:
            return self.response_error(320)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except VlanCantDeallocate, e:
            return self.response_error(293)
        except IpCantBeRemovedFromVip as e:
            return self.response_error(319, 'vlan', 'vlan', id_vlan)
        except VlanNotFoundError:
            return self.response_error(116)
        except (VlanError):
            return self.response_error(1)
        except Exception as e:
            self.log.exception('Failed to deallocate vlan.')
            if isinstance(e, IntegrityError):
                return self.response_error(356, id_vlan)
            else:
                return self.response_error(1)
