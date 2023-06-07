# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class ListConfigBGPNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = 'ListConfigBGP id = {} do not exist'.format(msg)


class ListConfigBGPError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class ListConfigBGPDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'ListConfigBGP does not exists'


class ListConfigBGPAssociatedToRouteMapEntryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, list_config_bgp):
        self.detail = 'ListConfigBGP id = {} is associated ' \
                      'in RouteMapEntries = {}'.\
            format(list_config_bgp.id, list_config_bgp.route_map_entries_id)


class ListConfigBGPIsDeployedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, list_config_bgp, neighbors_v4, neighbors_v6):
        self.detail = 'ListConfigBGP id = {} is deployed at ' \
                      'NeighborsV4 = {} and NeighborsV6 = {}'. \
            format(list_config_bgp.id,
                   map(int, neighbors_v4.values_list('id', flat=True)),
                   map(int, neighbors_v6.values_list('id', flat=True)))


class ListConfigBGPAlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, list_config_bgp):
        self.detail = 'ListConfigBGP {} is already deployed at equipment'. \
            format(list_config_bgp.id)


class ListConfigBGPNotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, list_config_bgp):
        self.detail = 'ListConfigBGP {} is not deployed at equipment'. \
            format(list_config_bgp.id)
