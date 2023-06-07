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
from rest_framework import status
from rest_framework.exceptions import APIException


class CommandErrorException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: Error applying command on equipment.' \
                     ' Equipment returned error status.'

    def __init__(self, msg=None):
        self.detail = 'Error: Error applying command on equipment. ' \
                      'Equipment returned error status. <<%s>>' % (msg)


class ConnectionException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed trying to connect to equipment.'


class CurrentlyBusyErrorException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Equipment is currenlty busy. ' \
                     'Failed trying to configure equipment.'


class InvalidCommandException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: Invalid command sent to equipment. ' \
                     'Please check template syntax or module used.'

    def __init__(self, msg=None):
        self.detail = 'Error: Invalid command sent to equipment. ' \
                      'Check syntax. Equipment msg: <<%s>>' % (msg)


class InvalidEquipmentAccessException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No access or multiple accesses found for equipment.'


class BGPTemplateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No BGP configuration templates found for equipments.'


class InvalidKeyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid key Exception.'


class InvalidFilenameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid filename.'

    def __init__(self, filename=None):
        self.detail = 'Invalid filename: %s' % (filename)


class LoadEquipmentModuleException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Could not load equipment module: '

    def __init__(self, module_name=None):
        self.detail = 'Could not load equipment module: %s' % (module_name)


class UnableToVerifyResponse(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: Could not match equipment response in any ' \
                     'known behavior. Please check config for status.'


class UnsupportedEquipmentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Tryed to apply configuration on unsupported ' \
                     'equipment interface.'


class UnsupportedVersion(APIException):
    """ Return message error: Version unsupported by plugin """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Version unsupported by plugin'

    def __init__(self, msg=None):
        self.detail = 'Version unsupported by plugin: <<%s>>' % (msg)


class PluginUninstanced(APIException):
    """Return message error: Plugin uninstanced"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Plugin uninstanced'

    def __init__(self, msg=None):
        self.detail = 'Plugin uninstanced: <<%s>>' % (msg)


class PluginNotConnected(APIException):
    """Return message error: Plugin uninstanced"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Plugin not connected'

    def __init__(self):
        self.detail = 'Plugin not connected'


class NamePropertyInvalid(APIException):
    """Return message error: Property Name is invalid"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Property Name is invalid'

    def __init__(self, msg=None):
        self.detail = 'Property Name is invalid: <<%s>>' % (msg)


class ValueInvalid(APIException):
    """Return message error: value is invalid"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Value is invalid'

    def __init__(self, msg=None):
        self.detail = 'Value is invalid: <<%s>>' % (msg)


class ControllerInventoryIsEmpty(APIException):
    """Returno message error: No Nodes on Controller Inventory"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'SDN Controller\'s inventory is empty'

    def __init__(self, msg=None):
        self.detail = 'SDN Controller\'s inventory is empty: <<%s>>' % (msg)
