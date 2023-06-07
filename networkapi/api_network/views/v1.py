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
import logging

from django.db.transaction import commit_on_success
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.admin_permission import AdminPermission
from networkapi.api_equipment.exceptions import AllEquipmentsAreInMaintenanceException
from networkapi.api_equipment.facade import all_equipments_are_in_maintenance
from networkapi.api_network import exceptions
from networkapi.api_network.facade import v1 as facade
from networkapi.api_network.models import DHCPRelayIPv4
from networkapi.api_network.models import DHCPRelayIPv6
from networkapi.api_network.permissions import DeployConfig
from networkapi.api_network.permissions import Read
from networkapi.api_network.permissions import Write
from networkapi.api_network.serializers.v1 import DHCPRelayIPv4Serializer
from networkapi.api_network.serializers.v1 import DHCPRelayIPv6Serializer
from networkapi.api_network.serializers.v1 import NetworkIPv4Serializer
from networkapi.api_network.serializers.v1 import NetworkIPv6Serializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6NotFoundError

log = logging.getLogger(__name__)


class DHCPRelayIPv4View(APIView):

    @permission_classes((IsAuthenticated, Read))
    def get(self, *args, **kwargs):
        """
        Lists DHCP relay ipv4 and filter by network or IP parameters.
        """
        try:

            networkipv4_id = ''
            ipv4_id = ''

            if self.request.QUERY_PARAMS.get('networkipv4'):
                networkipv4_id = int(self.request.QUERY_PARAMS['networkipv4'])
            if self.request.QUERY_PARAMS.get('ipv4'):
                ipv4_id = int(self.request.QUERY_PARAMS['ipv4'])

            dhcprelayipv4_obj = DHCPRelayIPv4.objects.all()

            if networkipv4_id is not '':
                dhcprelayipv4_obj = dhcprelayipv4_obj.filter(
                    networkipv4__id=networkipv4_id)
            if ipv4_id is not '':
                dhcprelayipv4_obj = dhcprelayipv4_obj.filter(ipv4__id=ipv4_id)

            serializer_options = DHCPRelayIPv4Serializer(
                dhcprelayipv4_obj,
                many=True
            )

            return Response(serializer_options.data)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException()

    @permission_classes((IsAuthenticated, Write))
    def post(self, *args, **kwargs):
        """
        Insert DHCP relay ipv4 and filter by network or IP parameters.
        """
        data = self.request.DATA
        if type(data) is list:
            raise exceptions.InvalidInputException()

        try:
            networkipv4_id = int(data['networkipv4'])
            ipv4_id = int(data['ipv4']['id'])
        except Exception, exception:
            raise exceptions.InvalidInputException()

        try:
            dhcprelay_obj = facade.create_dhcprelayIPv4_object(
                self.request.user, ipv4_id, networkipv4_id)

            serializer_options = DHCPRelayIPv4Serializer(
                dhcprelay_obj,
                many=False
            )

            return Response(serializer_options.data)

        except exceptions.DHCPRelayAlreadyExistsError, exception:
            raise exception
        except Exception, exception:
            log.error('Error: %s' % str(exception))
            raise api_exceptions.NetworkAPIException()


class DHCPRelayIPv4ByPkView(APIView):

    @permission_classes((IsAuthenticated, Read))
    def get(self, *args, **kwargs):
        """
        Lists dhcprelay ipv4 entry.
        """
        dhcprelay_id = kwargs['dhcprelay_id']
        dhcprelayipv4_obj = DHCPRelayIPv4.get_by_pk(id=dhcprelay_id)
        serializer_options = DHCPRelayIPv4Serializer(
            dhcprelayipv4_obj,
            many=False
        )
        return Response(serializer_options.data)

    @permission_classes((IsAuthenticated, Write))
    def delete(self, *args, **kwargs):
        """
        Delete dhcprelay ipv4 entry.
        """
        dhcprelay_id = kwargs['dhcprelay_id']
        facade.delete_dhcprelayipv4(self.request.user, dhcprelay_id)
        return Response({})


class DHCPRelayIPv6View(APIView):

    @permission_classes((IsAuthenticated, Read))
    def get(self, *args, **kwargs):
        """
        Lists DHCP relay ipv6 and filter by network or IP parameters.
        """
        try:

            networkipv6_id = ''
            ipv6_id = ''

            if self.request.QUERY_PARAMS.get('networkipv6'):
                networkipv6_id = int(self.request.QUERY_PARAMS['networkipv6'])
            if self.request.QUERY_PARAMS.get('ipv6'):
                ipv6_id = int(self.request.QUERY_PARAMS['ipv6'])

            dhcprelayipv6_obj = DHCPRelayIPv6.objects.all()

            if networkipv6_id is not '':
                dhcprelayipv6_obj = dhcprelayipv6_obj.filter(
                    networkipv6__id=networkipv6_id)
            if ipv6_id is not '':
                dhcprelayipv6_obj = dhcprelayipv6_obj.filter(ipv6__id=ipv6_id)

            serializer_options = DHCPRelayIPv6Serializer(
                dhcprelayipv6_obj,
                many=True
            )

            return Response(serializer_options.data)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException()

    @permission_classes((IsAuthenticated, Write))
    def post(self, *args, **kwargs):
        """
        Insert DHCP relay ipv6 and filter by network or IP parameters.
        """
        data = self.request.DATA
        if type(data) is list:
            raise exceptions.InvalidInputException()

        try:
            networkipv6_id = int(data['networkipv6'])
            ipv6_id = int(data['ipv6']['id'])
            log.info('DADOS %s %s' % (networkipv6_id, ipv6_id))
        except Exception, exception:
            raise exceptions.InvalidInputException()

        try:
            dhcprelay_obj = facade.create_dhcprelayIPv6_object(
                self.request.user, ipv6_id, networkipv6_id)

            serializer_options = DHCPRelayIPv6Serializer(
                dhcprelay_obj,
                many=False
            )

            return Response(serializer_options.data)

        except exceptions.DHCPRelayAlreadyExistsError, exception:
            raise exception
        except Exception, exception:
            log.error('Error: %s' % str(exception))
            raise api_exceptions.NetworkAPIException()


class DHCPRelayIPv6ByPkView(APIView):

    @permission_classes((IsAuthenticated, Read))
    def get(self, *args, **kwargs):
        """
        Lists DHCPrelay IPv6 entry.
        """
        dhcprelay_id = kwargs['dhcprelay_id']
        dhcprelayipv6_obj = DHCPRelayIPv6.get_by_pk(id=dhcprelay_id)
        serializer_options = DHCPRelayIPv6Serializer(
            dhcprelayipv6_obj,
            many=False
        )

        return Response(serializer_options.data)

    @permission_classes((IsAuthenticated, Write))
    def delete(self, *args, **kwargs):
        """
        Delete DHCPrelay IPv6 entry.
        """
        dhcprelay_id = kwargs['dhcprelay_id']
        facade.delete_dhcprelayipv6(self.request.user, dhcprelay_id)
        return Response({})


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv4(request):
    """
    Lists network ipv4 and filter by url parameters.
    """
    try:

        environment_vip = ''
        vlan_environment = ''

        if request.QUERY_PARAMS.get('environment_vip'):
            environment_vip = str(request.QUERY_PARAMS['environment_vip'])

        if request.QUERY_PARAMS.get('vlan_environment'):
            vlan_environment = str(request.QUERY_PARAMS['vlan_environment'])

        networkipv4_obj = NetworkIPv4.objects.all()

        if environment_vip:
            networkipv4_obj = networkipv4_obj.filter(
                ambient_vip__id=environment_vip)

        if vlan_environment:
            networkipv4_obj = networkipv4_obj.filter(
                vlan__ambiente=vlan_environment)

        serializer_options = NetworkIPv4Serializer(
            networkipv4_obj,
            many=True
        )

        return Response(serializer_options.data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv4_by_pk(request, network_id):
    """
    Lists network ipv4.
    """
    try:

        networkipv4_obj = NetworkIPv4.get_by_pk(network_id)
        serializer_options = NetworkIPv4Serializer(
            networkipv4_obj,
            many=False
        )

        return Response(serializer_options.data)

    except NetworkIPv4NotFoundError, exception:
        raise exceptions.InvalidNetworkIDException()
    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, Write, DeployConfig))
@commit_on_success
def networkIPv4_deploy(request, network_id):
    """Deploy network L3 configuration in the environment routers for network ipv4

    Receives optional parameter equipments to specify what equipment should
    receive network configuration
    """
    log.debug("networkIPv4_deploy")
    networkipv4 = NetworkIPv4.get_by_pk(int(network_id))
    environment = networkipv4.vlan.ambiente
    equipments_id_list = None
    if request.DATA is not None:
        equipments_id_list = request.DATA.get('equipments', None)

    if equipments_id_list is not None:
        if type(equipments_id_list) is not list:
            raise api_exceptions.ValidationException('equipments')

        for equip in equipments_id_list:
            try:
                int(equip)
            except ValueError:
                raise api_exceptions.ValidationException('equipments')

        # Check that equipments received as parameters are in correct vlan
        # environment
        equipment_list = Equipamento.objects.filter(
            equipamentoambiente__ambiente=environment,
            id__in=equipments_id_list)
        log.info('list = %s' % equipment_list)
        if len(equipment_list) != len(equipments_id_list):
            log.error(
                'Error: equipments %s are not part of network environment.' % equipments_id_list)
            raise exceptions.EquipmentIDNotInCorrectEnvException()
    else:
        # TODO GET network routers
        equipment_list = Equipamento.objects.filter(
            ipequipamento__ip__networkipv4=networkipv4,
            equipamentoambiente__ambiente=networkipv4.vlan.ambiente,
            equipamentoambiente__is_router=1).distinct()
        if len(equipment_list) == 0:
            raise exceptions.NoEnvironmentRoutersFoundException()

    # Check permission to configure equipments
    for equip in equipment_list:
        # User permission
        if not has_perm(request.user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None,
                        equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
            log.error('User does not have permission to perform the operation.')
            raise PermissionDenied(
                'No permission to configure equipment %s-%s' % (equip.id, equip.nome))

    if all_equipments_are_in_maintenance(equipment_list):
        raise AllEquipmentsAreInMaintenanceException()

    try:

        # deploy network configuration
        if request.method == 'POST':
            returned_data = facade.deploy_networkIPv4_configuration(
                request.user, networkipv4, equipment_list)
        elif request.method == 'DELETE':
            returned_data = facade.remove_deploy_networkIPv4_configuration(
                request.user, networkipv4, equipment_list)

        return Response(returned_data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv6(request):
    """
    Lists network ipv6 and filter by url parameters.
    """

    try:

        environment_vip = ''
        vlan_environment = ''

        if request.QUERY_PARAMS.get('environment_vip'):
            environment_vip = str(request.QUERY_PARAMS['environment_vip'])

        if request.QUERY_PARAMS.get('vlan_environment'):
            vlan_environment = str(request.QUERY_PARAMS['vlan_environment'])

        networkipv6_obj = NetworkIPv6.objects.all()

        if environment_vip:
            networkipv6_obj = networkipv6_obj.filter(
                ambient_vip__id=environment_vip)

        if vlan_environment:
            networkipv6_obj = networkipv6_obj.filter(
                vlan__ambiente=vlan_environment)

        serializer_options = NetworkIPv6Serializer(
            networkipv6_obj,
            many=True
        )

        return Response(serializer_options.data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv6_by_pk(request, network_id):
    """
    Lists network ipv6.
    """
    try:

        networkipv6_obj = NetworkIPv6.get_by_pk(network_id)

        serializer_options = NetworkIPv6Serializer(
            networkipv6_obj,
            many=False
        )

        return Response(serializer_options.data)
    except NetworkIPv6NotFoundError, exception:
        raise exceptions.InvalidNetworkIDException()
    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, Write, DeployConfig))
@commit_on_success
def networkIPv6_deploy(request, network_id):
    """Deploy network L3 configuration in the environment routers for network ipv6

    Receives optional parameter equipments to specify what equipment should
    receive network configuration
    """

    networkipv6 = NetworkIPv6.get_by_pk(int(network_id))
    environment = networkipv6.vlan.ambiente
    equipments_id_list = None
    if request.DATA is not None:
        equipments_id_list = request.DATA.get('equipments', None)

    equipment_list = []

    if equipments_id_list is not None:
        if type(equipments_id_list) is not list:
            raise api_exceptions.ValidationException('equipments')

        for equip in equipments_id_list:
            try:
                int(equip)
            except ValueError:
                raise api_exceptions.ValidationException('equipments')

        # Check that equipments received as parameters are in correct vlan
        # environment
        equipment_list = Equipamento.objects.filter(
            equipamentoambiente__ambiente=environment,
            id__in=equipments_id_list)
        log.info('list = %s' % equipment_list)
        if len(equipment_list) != len(equipments_id_list):
            log.error(
                'Error: equipments %s are not part of network environment.' % equipments_id_list)
            raise exceptions.EquipmentIDNotInCorrectEnvException()
    else:
        # TODO GET network routers
        equipment_list = Equipamento.objects.filter(
            ipv6equipament__ip__networkipv6=networkipv6,
            equipamentoambiente__ambiente=networkipv6.vlan.ambiente,
            equipamentoambiente__is_router=1).distinct()
        if len(equipment_list) == 0:
            raise exceptions.NoEnvironmentRoutersFoundException()

    # Check permission to configure equipments
    for equip in equipment_list:
        # User permission
        if not has_perm(request.user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
            log.error('User does not have permission to perform the operation.')
            raise PermissionDenied(
                'No permission to configure equipment %s-%s' % (equip.id, equip.nome))

    if all_equipments_are_in_maintenance(equipment_list):
        raise AllEquipmentsAreInMaintenanceException()

    try:
        # deploy network configuration
        if request.method == 'POST':
            returned_data = facade.deploy_networkIPv6_configuration(
                request.user, networkipv6, equipment_list)
        elif request.method == 'DELETE':
            returned_data = facade.remove_deploy_networkIPv6_configuration(
                request.user, networkipv6, equipment_list)

        return Response(returned_data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()
