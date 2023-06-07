# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class RouteMapNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = 'RouteMap id = {} do not exist' .format(msg)


class RouteMapError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class RouteMapDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'RouteMap does not exists'


class RouteMapEntryNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = 'RouteMapEntry id = {} do not exist'.format(msg)


class RouteMapEntryError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class RouteMapEntryDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'RouteMapEntry does not exists'


class RouteMapAssociatedToRouteMapEntryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map):
        self.detail = 'RouteMap id = {} is associated ' \
                      'with RouteMapEntries ids = {}'. \
            format(route_map.id, route_map.route_map_entries_id)


class RouteMapAssociatedToPeerGroupException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map):
        self.detail = 'RouteMap id = {} is associated ' \
                      'with PeerGroups ids = {}'. \
            format(route_map.id, route_map.peer_groups_id)


class RouteMapIsDeployedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map, neighbors_v4, neighbors_v6):
        self.detail = 'RouteMap id = {} is deployed at NeighborsV4 id = {} ' \
                      'and NeighborsV6 id = {}'. \
            format(route_map.id,
                   map(int, neighbors_v4.values_list('id', flat=True)),
                   map(int, neighbors_v6.values_list('id', flat=True)))


class RouteMapAlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map):
        self.detail = 'RouteMap {} is already deployed at equipment'.\
            format(route_map.id)


class RouteMapNotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map):
        self.detail = 'RouteMap {} is not deployed at equipment'. \
            format(route_map.id)


class AssociatedListsConfigBGPAreNotDeployedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, lists_config_bgp):
        self.detail = 'Lists Config BGP with ids = {} are not deployed'. \
            format(lists_config_bgp)


class RouteMapEntryDuplicatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map_entry):
        self.detail = 'It already exists RouteMapEntry with ListConfigBGP ' \
                      'id = {}'.\
            format(route_map_entry.list_config_bgp, route_map_entry.route_map)


class RouteMapEntryWithDeployedRouteMapException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map_entry, neighbors_v4, neighbors_v6):
        self.detail = 'RouteMap id = {} is deployed at ' \
                      'NeighborsV4 = {} and NeighborsV6 = {}'. \
            format(route_map_entry.route_map,
                   map(int, neighbors_v4.values_list('id', flat=True)),
                   map(int, neighbors_v6.values_list('id', flat=True)))
