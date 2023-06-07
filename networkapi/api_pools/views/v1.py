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
import json
import logging
from datetime import datetime

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.transaction import commit_on_success
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import EnvironmentEnvironmentVip
from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_pools import exceptions
from networkapi.api_pools.facade import delete_environment_option_pool
from networkapi.api_pools.facade import delete_option_pool
from networkapi.api_pools.facade import exec_script_check_poolmember_by_pool
from networkapi.api_pools.facade import get_or_create_healthcheck
from networkapi.api_pools.facade import manager_pools
from networkapi.api_pools.facade import prepare_to_save_reals
from networkapi.api_pools.facade import save_environment_option_pool
from networkapi.api_pools.facade import save_option_pool
from networkapi.api_pools.facade import save_server_pool
from networkapi.api_pools.facade import save_server_pool_member
from networkapi.api_pools.facade import update_environment_option_pool
from networkapi.api_pools.facade import update_option_pool
from networkapi.api_pools.models import OpcaoPoolAmbiente
from networkapi.api_pools.models import OptionPool
from networkapi.api_pools.models import OptionPoolEnvironment
from networkapi.api_pools.permissions import Read
from networkapi.api_pools.permissions import ScriptAlterPermission
from networkapi.api_pools.permissions import ScriptCreatePermission
from networkapi.api_pools.permissions import ScriptRemovePermission
from networkapi.api_pools.permissions import Write
from networkapi.api_pools.serializers.v1 import AmbienteSerializer
from networkapi.api_pools.serializers.v1 import EquipamentoSerializer
from networkapi.api_pools.serializers.v1 import HealthcheckSerializer
from networkapi.api_pools.serializers.v1 import OpcaoPoolAmbienteSerializer
from networkapi.api_pools.serializers.v1 import OptionPoolEnvironmentSerializer
from networkapi.api_pools.serializers.v1 import OptionPoolSerializer
from networkapi.api_pools.serializers.v1 import PoolSerializer
from networkapi.api_pools.serializers.v1 import ServerPoolDatatableSerializer
from networkapi.api_pools.serializers.v1 import ServerPoolMemberSerializer
from networkapi.api_pools.serializers.v1 import ServerPoolSerializer
from networkapi.api_pools.serializers.v1 import VipPortToPoolSerializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.equipamento.models import Equipamento
from networkapi.error_message_utils import error_messages
from networkapi.exception import InvalidValueError
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import Ipv6
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.requisicaovips.models import VipPortToPool
from networkapi.util import is_valid_healthcheck_destination
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_list_int_greater_zero_param
from networkapi.util import is_valid_option
from networkapi.util import is_valid_pool_identifier_text
from networkapi.util import is_valid_string_maxsize

log = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def pool_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    try:

        data = dict()
        environment_id = request.DATA.get('environment_id')
        start_record = request.DATA.get('start_record')
        end_record = request.DATA.get('end_record')
        asorting_cols = request.DATA.get('asorting_cols')
        searchable_columns = request.DATA.get('searchable_columns')
        custom_search = request.DATA.get('custom_search')

        if not is_valid_int_greater_zero_param(environment_id, False):
            raise api_exceptions.ValidationException('Environment id invalid.')

        query_pools = ServerPool.objects.all()

        if environment_id:
            query_pools = query_pools.filter(environment=environment_id)

        server_pools, total = build_query_to_datatable(
            query_pools,
            asorting_cols,
            custom_search,
            searchable_columns,
            start_record,
            end_record
        )

        serializer_pools = ServerPoolDatatableSerializer(
            server_pools,
            many=True
        )

        data['pools'] = serializer_pools.data
        data['total'] = total

        return Response(data)

    except api_exceptions.ValidationException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def pool_list_by_reqvip(request):
    """
    List all code snippets, or create a new snippet.
    """
    try:

        data = dict()

        id_vip = request.DATA.get('id_vip')
        start_record = request.DATA.get('start_record')
        end_record = request.DATA.get('end_record')
        asorting_cols = request.DATA.get('asorting_cols')
        searchable_columns = request.DATA.get('searchable_columns')
        custom_search = request.DATA.get('custom_search')

        if not is_valid_int_greater_zero_param(id_vip, False):
            raise api_exceptions.ValidationException('Vip id invalid.')

        query_pools = ServerPool.objects.filter(
            vipporttopool__requisicao_vip__id=id_vip)

        server_pools, total = build_query_to_datatable(
            query_pools,
            asorting_cols,
            custom_search,
            searchable_columns,
            start_record,
            end_record
        )

        serializer_pools = ServerPoolDatatableSerializer(
            server_pools,
            many=True
        )

        data['pools'] = serializer_pools.data
        data['total'] = total

        return Response(data)

    except api_exceptions.ValidationException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def list_all_members_by_pool(request, id_server_pool):
    try:

        if not is_valid_int_greater_zero_param(id_server_pool):
            raise exceptions.InvalidIdPoolException()

        data = dict()
        start_record = request.DATA.get('start_record')
        end_record = request.DATA.get('end_record')
        asorting_cols = request.DATA.get('asorting_cols')
        searchable_columns = request.DATA.get('searchable_columns')
        custom_search = request.DATA.get('custom_search')

        query_pools = ServerPoolMember.objects.filter(
            server_pool=id_server_pool)
        total = query_pools.count()

        checkstatus = False
        if 'checkstatus' in request.QUERY_PARAMS and request.QUERY_PARAMS['checkstatus'].upper() == 'TRUE':
            checkstatus = True

        if total > 0 and checkstatus:
            stdout = exec_script_check_poolmember_by_pool(id_server_pool)
            script_out = json.loads(stdout)

            if id_server_pool not in script_out.keys() or len(script_out[id_server_pool]) != total:
                raise exceptions.ScriptCheckStatusPoolMemberException(
                    detail='Script did not return as expected.')

            for pm in query_pools:
                member_checked_status = script_out[id_server_pool][str(pm.id)]
                if member_checked_status not in range(0, 8):
                    raise exceptions.ScriptCheckStatusPoolMemberException(
                        detail='Status script did not return as expected.')

                # Save to BD
                pm.member_status = member_checked_status
                pm.last_status_update = datetime.now()
                pm.save(request.user)

        server_pools, total = build_query_to_datatable(
            query_pools,
            asorting_cols,
            custom_search,
            searchable_columns,
            start_record,
            end_record
        )

        serializer_pools = ServerPoolMemberSerializer(server_pools, many=True)

        data['server_pool_members'] = serializer_pools.data
        data['total'] = total

        return Response(data)

    except exceptions.InvalidIdPoolException, exception:
        log.exception(exception)
        raise exception

    except ServerPool.DoesNotExist, exception:
        log.exception(exception)
        raise exceptions.PoolDoesNotExistException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def get_equipamento_by_ip(request, id_ip):
    try:

        if not is_valid_int_greater_zero_param(id_ip):
            raise exceptions.InvalidIdPoolException()

        data = dict()

        try:
            ipequips_obj = IpEquipamento.objects.filter(
                ip=id_ip).uniqueResult()
            equip = Equipamento.get_by_pk(pk=ipequips_obj.equipamento_id)

            serializer_equipamento = EquipamentoSerializer(equip, many=False)

            data['equipamento'] = serializer_equipamento.data
        except ObjectDoesNotExist, exception:
            pass

        return Response(data)

    except exceptions.InvalidIdPoolException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write, ScriptAlterPermission))
@commit_on_success
def delete(request):
    """
    Delete Pools by list id.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:
            try:
                server_pool = ServerPool.objects.get(id=_id)

                if server_pool.pool_created is True:
                    raise exceptions.PoolConstraintCreatedException()

                if VipPortToPool.objects.filter(server_pool=_id):
                    raise exceptions.PoolConstraintVipException()

                for server_pool_member in server_pool.serverpoolmember_set.all():
                    server_pool_member.delete(request.user)

                server_pool.delete(request.user)

            except ServerPool.DoesNotExist:
                pass

        return Response()

    except exceptions.PoolConstraintVipException, exception:
        log.exception(exception)
        raise exception

    except exceptions.ScriptDeletePoolException, exception:
        log.exception(exception)
        raise exception

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptDeletePoolException()

    except ValueError, exception:
        log.exception(exception)
        raise exceptions.InvalidIdPoolException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ScriptRemovePermission))
@commit_on_success
def remove(request):
    """
    Remove Pools by list id running script and update to not created.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:
            try:

                server_pool = ServerPool.objects.get(id=_id)

                code, _, _ = exec_script(settings.POOL_REMOVE % _id)

                if code != 0:
                    raise exceptions.ScriptRemovePoolException()

                server_pool.pool_created = False
                server_pool.save(request.user)

            except ServerPool.DoesNotExist:
                pass

        return Response()

    except exceptions.ScriptRemovePoolException, exception:
        log.exception(exception)
        raise exception

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptRemovePoolException()

    except ValueError, exception:
        log.exception(exception)
        raise exceptions.InvalidIdPoolException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write, ScriptCreatePermission))
@commit_on_success
def create(request):
    """
    Create Pools by list id running script and update to created.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:

            server_pool = ServerPool.objects.get(id=_id)

            code, _, _ = exec_script(settings.POOL_CREATE % _id)

            if code != 0:
                raise exceptions.ScriptCreatePoolException()

            server_pool.pool_created = True
            server_pool.save(request.user)

        return Response()

    except ServerPool.DoesNotExist, exception:
        log.exception(exception)
        raise exceptions.PoolDoesNotExistException()

    except exceptions.ScriptCreatePoolException, exception:
        log.exception(exception)
        raise exception

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptCreatePoolException()

    except ValueError, exception:
        log.exception(exception)
        raise exceptions.InvalidIdPoolException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def healthcheck_list(request):
    try:
        data = dict()

        healthchecks = Healthcheck.objects.all()

        serializer_healthchecks = HealthcheckSerializer(
            healthchecks,
            many=True
        )

        data['healthchecks'] = serializer_healthchecks.data

        return Response(data)

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def get_by_pk(request, id_server_pool):
    try:

        if not is_valid_int_greater_zero_param(id_server_pool):
            raise exceptions.InvalidIdPoolException()

        data = dict()

        server_pool = ServerPool.objects.get(pk=id_server_pool)

        server_pool_members = ServerPoolMember.objects.filter(
            server_pool=id_server_pool
        )

        serializer_server_pool = ServerPoolSerializer(server_pool)

        serializer_server_pool_member = ServerPoolMemberSerializer(
            server_pool_members,
            many=True
        )

        data['server_pool'] = serializer_server_pool.data
        data['server_pool_members'] = serializer_server_pool_member.data

        return Response(data)

    except exceptions.InvalidIdPoolException, exception:
        log.exception(exception)
        raise exception

    except ServerPool.DoesNotExist, exception:
        log.exception(exception)
        raise exceptions.PoolDoesNotExistException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ScriptAlterPermission))
@commit_on_success
def enable(request):
    """
    Create Pools by list id running script and update to created.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:

            server_pool_member = ServerPoolMember.objects.get(id=_id)

            ipv4 = server_pool_member.ip
            ipv6 = server_pool_member.ipv6

            id_pool = server_pool_member.server_pool.id
            id_ip = ipv4 and ipv4.id or ipv6 and ipv6.id
            port_ip = server_pool_member.port_real

            command = settings.POOL_REAL_ENABLE % (id_pool, id_ip, port_ip)

            code, _, _ = exec_script(command)

            if code != 0:
                raise exceptions.ScriptEnablePoolException()

        return Response()

    except ServerPoolMember.DoesNotExist, exception:
        log.exception(exception)
        raise exceptions.PoolMemberDoesNotExistException()

    except exceptions.ScriptEnablePoolException, exception:
        log.exception(exception)
        raise exception

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptEnablePoolException()

    except ValueError, exception:
        log.exception(exception)
        raise exceptions.InvalidIdPoolMemberException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ScriptAlterPermission))
@commit_on_success
def disable(request):
    """
    Create Pools by list id running script and update to created.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:

            server_pool_member = ServerPoolMember.objects.get(id=_id)

            ipv4 = server_pool_member.ip
            ipv6 = server_pool_member.ipv6

            id_pool = server_pool_member.server_pool.id
            id_ip = ipv4 and ipv4.id or ipv6 and ipv6.id
            port_ip = server_pool_member.port_real

            command = settings.POOL_REAL_DISABLE % (id_pool, id_ip, port_ip)

            code, _, _ = exec_script(command)

            if code != 0:
                raise exceptions.ScriptDisablePoolException()

        return Response()

    except ServerPoolMember.DoesNotExist, exception:
        log.exception(exception)
        raise exceptions.PoolMemberDoesNotExistException()

    except exceptions.ScriptDisablePoolException, exception:
        log.exception(exception)
        raise exception

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptDisablePoolException()

    except ValueError, exception:
        log.exception(exception)
        raise exceptions.InvalidIdPoolMemberException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def get_opcoes_pool_by_ambiente(request):
    try:
        log.info('get_opcoes_pool_by_ambiente')

        id_ambiente = request.DATA.get('id_environment')

        data = dict()

        if not is_valid_int_greater_zero_param(id_ambiente):
            raise exceptions.InvalidIdEnvironmentException()

        query_opcoes = OpcaoPoolAmbiente.objects.filter(ambiente=id_ambiente)
        opcoes_serializer = OpcaoPoolAmbienteSerializer(
            query_opcoes, many=True)
        data['opcoes_pool'] = opcoes_serializer.data

        return Response(data)

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_by_environment(request, environment_id):
    try:

        data = dict()

        created = True

        if not is_valid_int_greater_zero_param(environment_id):
            raise api_exceptions.ValidationException('Environment id invalid.')

        environment_obj = Ambiente.objects.get(id=environment_id)

        query_pools = ServerPool.objects.filter(
            environment=environment_obj,
            pool_created=created
        )

        serializer_pools = ServerPoolDatatableSerializer(
            query_pools,
            many=True
        )

        data['pools'] = serializer_pools.data

        return Response(data)

    except Ambiente.DoesNotExist, exception:
        log.exception(exception)
        raise api_exceptions.ObjectDoesNotExistException(
            'Environment Does Not Exist.')

    except api_exceptions.ValidationException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def get_requisicoes_vip_by_pool(request, id_server_pool):
    try:
        data = dict()

        if not is_valid_int_greater_zero_param(id_server_pool):
            raise exceptions.InvalidIdPoolException()

        start_record = request.DATA.get('start_record')
        end_record = request.DATA.get('end_record')
        asorting_cols = request.DATA.get('asorting_cols')
        searchable_columns = request.DATA.get('searchable_columns')
        custom_search = request.DATA.get('custom_search')

        query_requisicoes = VipPortToPool.objects.filter(
            server_pool=id_server_pool)

        requisicoes, total = build_query_to_datatable(
            query_requisicoes,
            asorting_cols,
            custom_search,
            searchable_columns,
            start_record,
            end_record
        )

        requisicoes_serializer = VipPortToPoolSerializer(
            requisicoes, many=True)

        data['requisicoes_vip'] = requisicoes_serializer.data
        data['total'] = total

        return Response(data)

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_pool_members(request, pool_id):
    try:

        data = dict()

        if not is_valid_int_greater_zero_param(pool_id):
            raise exceptions.InvalidIdPoolException()

        pool_obj = ServerPool.objects.get(id=pool_id)

        query_pools = ServerPoolMember.objects.filter(server_pool=pool_obj)

        serializer_pools = ServerPoolMemberSerializer(query_pools, many=True)

        data['pool_members'] = serializer_pools.data

        return Response(data)

    except exceptions.InvalidIdPoolException, exception:
        log.exception(exception)
        raise exception

    except ServerPool.DoesNotExist, exception:
        log.exception(exception)
        raise exceptions.PoolDoesNotExistException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_by_environment_vip(request, environment_vip_id):
    try:

        env_vip = EnvironmentVip.objects.get(id=environment_vip_id)

        server_pool_query = ServerPool.objects.filter(
            Q(environment__vlan__networkipv4__ambient_vip=env_vip) |
            Q(environment__vlan__networkipv6__ambient_vip=env_vip)
        ).distinct().order_by('identifier')

        serializer_pools = PoolSerializer(server_pool_query, many=True)

        return Response(serializer_pools.data)

    except EnvironmentVip.DoesNotExist, exception:
        log.exception(exception)
        raise api_exceptions.ObjectDoesNotExistException(
            'Environment Vip Does Not Exist')

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write, ScriptAlterPermission))
@commit_on_success
def save_reals(request):
    try:
        id_server_pool = request.DATA.get('id_server_pool')

        id_pool_member = request.DATA.get('id_pool_member')
        ip_list_full = request.DATA.get('ip_list_full')
        priorities = request.DATA.get('priorities')
        ports_reals = request.DATA.get('ports_reals')
        nome_equips = request.DATA.get('nome_equips')
        id_equips = request.DATA.get('id_equips')
        weight = request.DATA.get('weight')

        # Get server pool data
        sp = ServerPool.objects.get(id=id_server_pool)

        # Prepare to save reals
        list_server_pool_member = prepare_to_save_reals(ip_list_full, ports_reals, nome_equips, priorities, weight,
                                                        id_pool_member, id_equips)

        # valid if reals can linked by environment/environment vip relationship
        # rule
        reals_can_associate_server_pool(sp, list_server_pool_member)

        # Save reals
        save_server_pool_member(request.user, sp, list_server_pool_member)
        return Response()

    except api_exceptions.EnvironmentEnvironmentVipNotBoundedException, exception:
        log.exception(exception)
        raise exception

    except exceptions.ScriptAddPoolException, exception:
        log.exception(exception)
        raise exception

    except exceptions.IpNotFoundByEnvironment, exception:
        log.exception(exception)
        raise exception

    except exceptions.InvalidRealPoolException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write, ScriptAlterPermission))
@commit_on_success
def save(request):
    try:
        id = request.DATA.get('id')
        identifier = request.DATA.get('identifier')
        default_port = request.DATA.get('default_port')
        environment = long(request.DATA.get('environment'))
        balancing = request.DATA.get('balancing')
        maxconn = request.DATA.get('maxcom')
        servicedownaction_id = request.DATA.get('servicedownaction')

        # id_pool_member is cleaned below
        id_pool_member = request.DATA.get('id_pool_member')
        ip_list_full = request.DATA.get('ip_list_full')
        priorities = request.DATA.get('priorities')
        ports_reals = request.DATA.get('ports_reals')
        nome_equips = request.DATA.get('nome_equips')
        id_equips = request.DATA.get('id_equips')
        weight = request.DATA.get('weight')

        # ADDING AND VERIFYING HEALTHCHECK
        healthcheck_type = request.DATA.get('healthcheck_type')
        healthcheck_request = request.DATA.get('healthcheck_request')
        healthcheck_expect = request.DATA.get('healthcheck_expect')
        healthcheck_destination = request.DATA.get('healthcheck_destination')

        # Servicedownaction was not given
        try:
            if servicedownaction_id is None:
                servicedownactions = OptionPool.get_all_by_type_and_environment(
                    'ServiceDownAction', environment)
                # assert isinstance((servicedownactions.filter(name='none')).id, object)
                servicedownaction = (servicedownactions.get(name='none'))
            else:
                servicedownaction = OptionPool.get_by_pk(servicedownaction_id)

        except ObjectDoesNotExist:
            log.warning('Service-Down-Action none option not found')
            raise exceptions.InvalidServiceDownActionException()

        except MultipleObjectsReturned:
            log.warning(
                'Multiple service-down-action entries found for the given parameters')
            raise exceptions.InvalidServiceDownActionException()

        # Check identifier is a valid text
        if not is_valid_pool_identifier_text(identifier):
            raise exceptions.InvalidIdentifierPoolException()

        # Valid duplicate server pool
        has_identifier = ServerPool.objects.filter(
            identifier=identifier, environment=environment)
        # Cleans id_pool_member. It should be used only with existing pool
        id_pool_member = ['' for x in id_pool_member]
        if id:
            # Existing pool member is only valid in existing pools. New pools
            # cannot  use them
            id_pool_member = request.DATA.get('id_pool_member')
            has_identifier = has_identifier.exclude(id=id)
        # current_healthcheck_id = ServerPool.objects.get(id=id).healthcheck.id
        # current_healthcheck = Healthcheck.objects.get(id=current_healthcheck_id)
        # healthcheck = current_healthcheck

        if has_identifier.count() > 0:
            raise exceptions.InvalidIdentifierAlreadyPoolException()

        # Valid fist caracter is not is number
        # if identifier[0].isdigit():
        #    raise exceptions.InvalidIdentifierFistDigitPoolException()

        healthcheck_identifier = ''
        if healthcheck_destination is None:
            healthcheck_destination = '*:*'

        if not is_valid_healthcheck_destination(healthcheck_destination):
            raise api_exceptions.NetworkAPIException()

        healthcheck = get_or_create_healthcheck(request.user, healthcheck_expect, healthcheck_type, healthcheck_request,
                                                healthcheck_destination, healthcheck_identifier)

        # Remove empty values from list
        id_pool_member_noempty = [x for x in id_pool_member if x != '']

        # Get environment
        env = Ambiente.objects.get(id=environment)

        # Save Server pool
        sp, old_healthcheck_id = save_server_pool(request.user, id, identifier, default_port, healthcheck, env,
                                                  balancing,
                                                  maxconn, id_pool_member_noempty, servicedownaction)

        # Prepare and valid to save reals
        list_server_pool_member = prepare_to_save_reals(ip_list_full, ports_reals, nome_equips, priorities, weight,
                                                        id_pool_member, id_equips)

        reals_can_associate_server_pool(sp, list_server_pool_member)

        # Save reals
        pool_member = save_server_pool_member(
            request.user, sp, list_server_pool_member)

        # Check if someone is using the old healthcheck
        # If not, delete it to keep the database clean
        if old_healthcheck_id is not None:
            pools_using_healthcheck = ServerPool.objects.filter(
                healthcheck=old_healthcheck_id).count()
            if pools_using_healthcheck == 0:
                Healthcheck.objects.get(
                    id=old_healthcheck_id).delete(request.user)

        # Return data
        data = dict()
        data['pool'] = sp.id
        serializer_server_pool = ServerPoolSerializer(sp)
        data['server_pool'] = serializer_server_pool.data
        serializer_server_pool_member = ServerPoolMemberSerializer(
            pool_member,
            many=True
        )
        data['server_pool_members'] = serializer_server_pool_member.data

        return Response(data, status=status.HTTP_201_CREATED)

    except (api_exceptions.EnvironmentEnvironmentVipNotBoundedException,
            exceptions.ScriptAddPoolException,
            exceptions.InvalidIdentifierAlreadyPoolException,
            exceptions.InvalidIdentifierFistDigitPoolException,
            exceptions.UpdateEnvironmentVIPException,
            exceptions.UpdateEnvironmentServerPoolMemberException,
            exceptions.IpNotFoundByEnvironment,
            exceptions.InvalidRealPoolException,
            exceptions.UpdateEnvironmentPoolCreatedException,
            exceptions.InvalidServiceDownActionException,
            exceptions.CreatedPoolIdentifierException,
            exceptions.ScriptAlterLimitPoolDiffMembersException,
            exceptions.ScriptAlterLimitPoolException,
            exceptions.ScriptCreatePoolException,
            exceptions.ScriptAlterPriorityPoolMembersException,
            exceptions.InvalidRealPoolException,
            exceptions.ScriptAlterServiceDownActionException,
            exceptions.InvalidIdentifierPoolException)as exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_environments_with_pools(request):
    try:

        environment_query = Ambiente.objects.filter(
            serverpool__environment__isnull=False).distinct()

        serializer_pools = AmbienteSerializer(environment_query, many=True)

        return Response(serializer_pools.data)

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise api_exceptions.ObjectDoesNotExistException(
            'Environment Vip Does Not Exist')

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read,))
def chk_status_poolmembers_by_pool(request, pool_id):
    try:

        if not is_valid_int_greater_zero_param(pool_id):
            raise exceptions.InvalidIdPoolException()

        pool_obj = ServerPool.objects.get(id=pool_id)

        stdout = exec_script_check_poolmember_by_pool(pool_obj.id)

        data = json.loads(stdout)

        return Response(data)

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptCheckStatusPoolMemberException()

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.PoolDoesNotExistException()

    except exceptions.InvalidIdPoolException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def chk_status_poolmembers_by_vip(request, vip_id):
    try:
        if not is_valid_int_greater_zero_param(vip_id):
            raise exceptions.InvalidIdVipException()

        list_pools = ServerPool.objects.filter(
            vipporttopool__requisicao_vip__id=vip_id)

        if len(list_pools) is 0:
            raise exceptions.PoolMemberDoesNotExistException()

        list_result = []
        for obj_pool in list_pools:
            list_sts_poolmembers = exec_script_check_poolmember_by_pool(
                obj_pool.id)
            list_result.append({obj_pool.id: list_sts_poolmembers})

        return Response(list_result)

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write, ScriptAlterPermission))
@commit_on_success
def management_pools(request):
    try:

        manager_pools(request)

        return Response()

    except exceptions.InvalidStatusPoolMemberException, exception:
        log.exception(exception)
        raise exception

    except (exceptions.ScriptManagementPoolException, ScriptError), exception:
        log.exception(exception)
        raise exceptions.ScriptManagementPoolException()

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.PoolDoesNotExistException()

    except exceptions.InvalidIdPoolException, exception:
        log.exception(exception)
        raise exception

    except exceptions.InvalidIdPoolMemberException, exception:
        log.exception(exception)
        raise exception

    except ValueError, exception:
        log.exception(exception)
        raise exceptions.InvalidIdPoolMemberException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_all_options(request):
    try:

        type = ''

        if 'type' in request.QUERY_PARAMS:
            type = str(request.QUERY_PARAMS['type'])

        options = OptionPool.objects.all()

        if type:
            options = options.filter(type=type)

        serializer_options = OptionPoolSerializer(
            options,
            many=True
        )

        return Response(serializer_options.data)

    except ObjectDoesNotExist, exception:
        log.exception(exception)
        raise exceptions.OptionPoolDoesNotExistException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_environment_environment_vip_related(request):

    try:
        environment_list = []

        env_list_net_v4_related = Ambiente.objects.filter(vlan__networkipv4__ambient_vip__id__isnull=False)\
            .order_by('divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome')\
            .select_related('grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter')\
            .distinct()

        env_list_net_v6_related = Ambiente.objects.filter(vlan__networkipv6__ambient_vip__id__isnull=False)\
            .order_by('divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome')\
            .select_related('grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter')\
            .distinct()

        environment_list.extend(env_list_net_v4_related)
        environment_list.extend(env_list_net_v6_related)
        environment_list = set(environment_list)

        environment_list_dict = []

        for environment in environment_list:
            env_map = model_to_dict(environment)
            env_map['grupo_l3_name'] = environment.grupo_l3.nome
            env_map['ambiente_logico_name'] = environment.ambiente_logico.nome
            env_map['divisao_dc_name'] = environment.divisao_dc.nome
            if environment.filter is not None:
                env_map['filter_name'] = environment.filter.name

            environment_list_dict.append(env_map)

        return Response(environment_list_dict)

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def __list_option_by_pk_get(request, option_id):
    try:

        options = OptionPool.objects.get(id=option_id)
        serializer_options = OptionPoolSerializer(
            options,
            many=False
        )

        return Response(serializer_options.data)

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.OptionPoolDoesNotExistException

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, Write, ScriptAlterPermission))
@commit_on_success
def __delete_pool_option(request, option_id):
    """
    Delete options Pools by id.
    """

    try:

        OptionPool.objects.get(id=option_id)

        try:
            # TODO AFTER INTEGRATION MODEL OPTIONPOOL
            # if ServerPool.objects.filter(healthcheck=option_id):
            #    raise exceptions.OptionPoolConstraintPoolException()

            if ServerPool.objects.filter(servicedownaction=option_id):
                raise exceptions.OptionPoolConstraintPoolException()

            po = delete_option_pool(request.user, option_id)

            return Response({'id': po})

        except ObjectDoesNotExist:
            pass

    except exceptions.OptionPoolConstraintPoolException, exception:
        log.exception(exception)
        raise exception

    except exceptions.ScriptDeletePoolOptionException, exception:
        log.exception(exception)
        raise exception

    except ScriptError, exception:
        log.exception(exception)
        raise exceptions.ScriptDeletePoolException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['PUT'])
@permission_classes((IsAuthenticated, Write, ScriptAlterPermission))
@commit_on_success
def __modify_pool_option(request, option_id):
    """
    Delete options Pools by id.
    """
    try:

        OptionPool.objects.get(id=option_id)

        try:
            type = request.DATA.get('type')
            description = request.DATA.get('name')

            # tipo_opcao can NOT be greater than 50
            if not is_valid_string_maxsize(type, 50, True) or not is_valid_option(type):
                log.error(
                    'Parameter tipo_opcao is invalid. Value: %s.', type)
                raise InvalidValueError(None, 'type', type)

            # nome_opcao_txt can NOT be greater than 50
            if not is_valid_string_maxsize(description, 50, True) or not is_valid_option(description):
                log.error(
                    'Parameter nome_opcao_txt is invalid. Value: %s.', description)
                raise InvalidValueError(None, 'name', description)

            po = update_option_pool(request.user, option_id, type, description)

            serializer_options = OptionPoolSerializer(
                po,
                many=False
            )

        except ObjectDoesNotExist:
            pass

        return Response(serializer_options.data)

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.OptionPoolDoesNotExistException

    except exceptions.ScriptModifyPoolOptionException, exception:
        log.exception(exception)
        raise exception

    except exceptions.OptionPoolConstraintPoolException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, Read, Write, ScriptAlterPermission))
def list_option_by_pk(request, option_id):
    if request.method == 'GET':
        return __list_option_by_pk_get(request, option_id)
    elif request.method == 'DELETE':
        return __delete_pool_option(request, option_id)
    elif request.method == 'PUT':
        return __modify_pool_option(request, option_id)


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def save_pool_option(request):
    try:

        # log.warning("RECEBEU %s" % request.DATA)
        type = request.DATA.get('type')
        description = request.DATA.get('name')

        # tipo_opcao can NOT be greater than 50
        if not is_valid_string_maxsize(type, 50, True) or not is_valid_option(type):
            log.error(
                'Parameter tipo_opcao is invalid. Value: %s.', type)
            raise InvalidValueError(None, 'type', type)

        # nome_opcao_txt can NOT be greater than 50
        if not is_valid_string_maxsize(description, 50, True) or not is_valid_option(description):
            log.error(
                'Parameter nome_opcao_txt is invalid. Value: %s.', description)
            raise InvalidValueError(None, 'name', description)

        po = save_option_pool(request.user, type, description)

        serializer_options = OptionPoolSerializer(
            po,
            many=False
        )

        return Response(serializer_options.data)

    except exceptions.ScriptAddPoolOptionException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_all_environment_options(request):
    try:
        environment_id = ''
        option_id = ''
        option_type = ''

        if 'environment_id' in request.QUERY_PARAMS:
            environment_id = int(request.QUERY_PARAMS['environment_id'])

        if 'option_id' in request.QUERY_PARAMS:
            option_id = int(request.QUERY_PARAMS['option_id'])

        if 'option_type' in request.QUERY_PARAMS:
            option_type = str(request.QUERY_PARAMS['option_type'])

        environment_options = OptionPoolEnvironment.objects.all()

        if environment_id:
            environment_options = environment_options.filter(
                environment=environment_id)

        if option_id:
            environment_options = environment_options.filter(option=option_id)

        if option_type:
            environment_options = environment_options.filter(
                option__type=option_type)

        serializer_options = OptionPoolEnvironmentSerializer(
            environment_options,
            many=True
        )

        return Response(serializer_options.data)

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def __list_environment_options_by_pk(request, environment_option_id):
    try:

        environment_options = OptionPoolEnvironment.objects.get(
            id=environment_option_id)

        serializer_options = OptionPoolEnvironmentSerializer(
            environment_options,
            many=False
        )

        return Response(serializer_options.data)

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.OptionPoolEnvironmentDoesNotExistException

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def get_available_ips_to_add_server_pool(request, equip_name, id_ambiente):

    # Start with alls
    # Get Equipment

    lista_ips_equip, lista_ipsv6_equip = _get_available_ips_to_add_server_pool(
        equip_name, id_ambiente)
    # lists and dicts for return

    lista_ip_entregue = list()
    lista_ip6_entregue = list()

    for ip in lista_ips_equip:
        dict_ips4 = dict()
        dict_network = dict()

        dict_ips4['id'] = ip.id
        dict_ips4['ip'] = '%s.%s.%s.%s' % (
            ip.oct1, ip.oct2, ip.oct3, ip.oct4)

        dict_network['id'] = ip.networkipv4_id
        dict_network['network'] = '%s.%s.%s.%s' % (
            ip.networkipv4.oct1, ip.networkipv4.oct2, ip.networkipv4.oct3, ip.networkipv4.oct4)
        dict_network['mask'] = '%s.%s.%s.%s' % (
            ip.networkipv4.mask_oct1, ip.networkipv4.mask_oct2, ip.networkipv4.mask_oct3, ip.networkipv4.mask_oct4)

        dict_ips4['network'] = dict_network

        lista_ip_entregue.append(dict_ips4)

    for ip in lista_ipsv6_equip:
        dict_ips6 = dict()
        dict_network = dict()

        dict_ips6['id'] = ip.id
        dict_ips6['ip'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)

        dict_network['id'] = ip.networkipv6.id
        dict_network['network'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.networkipv6.block1, ip.networkipv6.block2, ip.networkipv6.block3, ip.networkipv6.block4, ip.networkipv6.block5, ip.networkipv6.block6, ip.networkipv6.block7, ip.networkipv6.block8)
        dict_network['mask'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.networkipv6.block1, ip.networkipv6.block2, ip.networkipv6.block3, ip.networkipv6.block4, ip.networkipv6.block5, ip.networkipv6.block6, ip.networkipv6.block7, ip.networkipv6.block8)

        dict_ips6['network'] = dict_network

        lista_ip6_entregue.append(dict_ips6)

    lista_ip_entregue = lista_ip_entregue if len(
        lista_ip_entregue) > 0 else None
    lista_ip6_entregue = lista_ip6_entregue if len(
        lista_ip6_entregue) > 0 else None

    return Response({'list_ipv4': lista_ip_entregue, 'list_ipv6': lista_ip6_entregue})


def _get_available_ips_to_add_server_pool(equip_name, id_ambiente):

    equip = Equipamento.get_by_name(equip_name)

    lista_ips_equip = set()
    lista_ipsv6_equip = set()

    environment_vip_list = EnvironmentVip.get_environment_vips_by_environment_id(
        id_ambiente)
    environment_list_related = EnvironmentEnvironmentVip.get_environment_list_by_environment_vip_list(
        environment_vip_list)

    # # Get all IPV4's Equipment
    for environment in environment_list_related:
        for ipequip in equip.ipequipamento_set.select_related('ambiente').all():
            network_ipv4 = ipequip.ip.networkipv4
            if network_ipv4.vlan.ambiente == environment:
                lista_ips_equip.add(ipequip.ip)

    # # Get all IPV6's Equipment
    for environment in environment_list_related:
        for ipequip in equip.ipv6equipament_set.select_related('ambiente').all():
            network_ipv6 = ipequip.ip.networkipv6
            if network_ipv6.vlan.ambiente == environment:
                lista_ipsv6_equip.add(ipequip.ip)

    return lista_ips_equip, lista_ipsv6_equip


def _get_server_pool_member_ipv4_ipv6(list_server_pool_member):

    ipv4_list = []
    ipv6_list = []

    for spm in list_server_pool_member:
        ip = spm.get('ip')
        ip_id = spm.get('id')

        if len(ip) <= 15:
            ipv4 = Ip.get_by_pk(ip_id)
            ipv4_list.append(ipv4)
        else:
            ipv6 = Ipv6.get_by_pk(ip_id)
            ipv6_list.append(ipv6)

    return ipv4_list, ipv6_list


def reals_can_associate_server_pool(server_pool, list_server_pool_member):

    try:
        environment_vip_list = EnvironmentVip.get_environment_vips_by_environment_id(
            server_pool.environment.id)
        environment_vip_list_name = ', '.join(
            [envvip.name for envvip in environment_vip_list])

        environment_list_related = EnvironmentEnvironmentVip.get_environment_list_by_environment_vip_list(
            environment_vip_list)

        ipv4_list, ipv6_list = _get_server_pool_member_ipv4_ipv6(
            list_server_pool_member)

        for ipv4 in ipv4_list:
            environment = Ambiente.objects.filter(
                vlan__networkipv4__ip=ipv4).uniqueResult()
            if environment not in environment_list_related:
                raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException(
                    error_messages.get(396) % (
                        environment.name, ipv4.ip_formated, environment_vip_list_name)
                )

        for ipv6 in ipv6_list:
            environment = Ambiente.objects.filter(
                vlan__networkipv6__ipv6=ipv6).uniqueResult()
            if environment not in environment_list_related:
                raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException(
                    error_messages.get(396) % (
                        server_pool.environment.name, ipv6.ip_formated, environment_vip_list_name)
                )

    except Exception, error:
        log.exception(error)
        raise error


def __update_environment_options_by_pk(request, environment_option_id):
    try:

        OptionPoolEnvironment.objects.get(id=environment_option_id)

        try:

            option_id = request.DATA.get('option_id')
            environment_id = request.DATA.get('environment_id')

            try:
                OptionPool.objects.get(id=option_id)
            except ObjectDoesNotExist, exception:
                log.error(exception)
                raise exceptions.OptionPoolDoesNotExistException
            try:
                Ambiente.objects.get(id=environment_id)
            except ObjectDoesNotExist, exception:
                log.error(exception)
                raise exceptions.EnvironmentDoesNotExistException

            epo = update_environment_option_pool(
                request.user, environment_option_id, option_id, environment_id)

            serializer_options = OptionPoolEnvironmentSerializer(
                epo,
                many=False
            )

            return Response(serializer_options.data)

        except ObjectDoesNotExist:
            pass

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.OptionPoolEnvironmentDoesNotExistException

    except exceptions.ScriptModifyEnvironmentPoolOptionException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


def __delete_environment_options_by_pk(request, environment_option_id):

    try:

        OptionPoolEnvironment.objects.get(id=environment_option_id)

        try:
            depo = delete_environment_option_pool(
                request.user, environment_option_id)

            return Response({'id': depo})

        except ObjectDoesNotExist:
            pass

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.OptionPoolEnvironmentDoesNotExistException

    except exceptions.ScriptDeleteEnvironmentPoolOptionException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, Read, Write, ScriptAlterPermission))
def environment_options_by_pk(request, environment_option_id):
    if request.method == 'GET':
        return __list_environment_options_by_pk(request, environment_option_id)
    elif request.method == 'DELETE':
        return __delete_environment_options_by_pk(request, environment_option_id)
    elif request.method == 'PUT':
        return __update_environment_options_by_pk(request, environment_option_id)


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def save_environment_options(request):
    try:

        option_id = request.DATA.get('option_id')
        environment_id = request.DATA.get('environment_id')

        try:
            OptionPool.objects.get(id=option_id)
        except ObjectDoesNotExist, exception:
            log.error(exception)
            raise exceptions.OptionPoolDoesNotExistException
        try:
            Ambiente.objects.get(id=environment_id)
        except ObjectDoesNotExist, exception:
            log.error(exception)
            raise exceptions.EnvironmentDoesNotExistException

        epo = save_environment_option_pool(
            request.user, option_id, environment_id)

        serializer_options = OptionPoolEnvironmentSerializer(
            epo,
            many=False
        )

        return Response(serializer_options.data)

    except exceptions.ScriptAddEnvironmentPoolOptionException, exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()
