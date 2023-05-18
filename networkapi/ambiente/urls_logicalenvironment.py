# # -*- coding: utf-8 -*-
# from __future__ import absolute_import

# from django.conf.urls import patterns
# from django.conf.urls import url

# from networkapi.ambiente.resource.LogicalEnvironmentAddResource import LogicalEnvironmentAddResource
# from networkapi.ambiente.resource.LogicalEnvironmentAlterRemoveResource import LogicalEnvironmentAlterRemoveResource
# from networkapi.ambiente.resource.LogicalEnvironmentGetAllResource import LogicalEnvironmentGetAllResource

# logical_environment_add_resource = LogicalEnvironmentAddResource()
# logical_environment_alter_remove_resource = LogicalEnvironmentAlterRemoveResource()
# logical_environment_get_all_resource = LogicalEnvironmentGetAllResource()

# urlpatterns = patterns(
#     '',
#     url(r'^$', logical_environment_add_resource.handle_request,
#         name='logical_environment.add'),
#     url(r'^all/$', logical_environment_get_all_resource.handle_request,
#         name='logical_environment.get.all'),
#     url(r'^(?P<id_logicalenvironment>[^/]+)/$', logical_environment_alter_remove_resource.handle_request,
#         name='logical_environment.update.remove.by.pk')
# )

#new

# -*- coding: utf-8 -*-
from django.urls import re_path

from networkapi.ambiente.resource.LogicalEnvironmentAddResource import LogicalEnvironmentAddResource
from networkapi.ambiente.resource.LogicalEnvironmentAlterRemoveResource import LogicalEnvironmentAlterRemoveResource
from networkapi.ambiente.resource.LogicalEnvironmentGetAllResource import LogicalEnvironmentGetAllResource

logical_environment_add_resource = LogicalEnvironmentAddResource()
logical_environment_alter_remove_resource = LogicalEnvironmentAlterRemoveResource()
logical_environment_get_all_resource = LogicalEnvironmentGetAllResource()

urlpatterns = [
    re_path(r'^$', logical_environment_add_resource.handle_request,
        name='logical_environment.add'),
    re_path(r'^all/$', logical_environment_get_all_resource.handle_request,
        name='logical_environment.get.all'),
    re_path(r'^(?P<id_logicalenvironment>[^/]+)/$', logical_environment_alter_remove_resource.handle_request,
        name='logical_environment.update.remove.by.pk')
]
