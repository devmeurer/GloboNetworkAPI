# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock, LOCK_SCRIPT
from networkapi.exception import InvalidValueError
from networkapi.roteiro.models import Roteiro, TipoRoteiro,TipoRoteiroNotFoundError, RoteiroError, RoteiroNotFoundError, RoteiroNameDuplicatedError, RoteiroHasEquipamentoError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_minsize, is_valid_string_maxsize

class ScriptAlterRemoveResource(RestResource):

    log = Log('ScriptAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Script.

        URL: script/<id_script>/
        """
        try:
            
            self.log.info("Edit Script")
            
            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            id_script = kwargs.get('id_script') 
            
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            script_map = networkapi_map.get('script')
            if script_map is None:
                return self.response_error(3, u'There is no value to the script tag  of XML request.')
            
            # Get XML data
            script = script_map.get('script')
            id_script_type = script_map.get('id_script_type')
            description = script_map.get('description')
            
            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)
            
            #Valid Script
            if not is_valid_string_minsize(script, 3) or not is_valid_string_maxsize(script, 40):
                self.log.error(u'Parameter script is invalid. Value: %s',script)
                raise InvalidValueError(None,'script',script)
            
            # Valid ID Script Type
            if not is_valid_int_greater_zero_param(id_script_type):
                self.log.error(u'The id_script_type parameter is not a valid value: %s.', id_script_type)
                raise InvalidValueError(None, 'id_script_type', id_script_type)
            
            #Valid description
            if not is_valid_string_minsize(description, 3) or not is_valid_string_maxsize(description, 100):
                self.log.error(u'Parameter description is invalid. Value: %s',description)
                raise InvalidValueError(None,'description',description)
            
            # Find Script by ID to check if it exist
            scr = Roteiro.get_by_pk(id_script)
            
            # Find Script Type by ID to check if it exist
            script_type = TipoRoteiro.get_by_pk(id_script_type)
            
            with distributedlock(LOCK_SCRIPT % id_script):
                
                try:
                    if not (scr.roteiro.lower() == script.lower() and scr.tipo_roteiro.id == id_script_type ):
                        Roteiro.get_by_name_script(script, id_script_type)
                        raise RoteiroNameDuplicatedError(None, u'Já existe um roteiro com o nome %s com tipo de roteiro %s.' % (script, script_type.tipo ))
                except RoteiroNotFoundError:
                    pass
                
            
                # set variables
                scr.roteiro = script
                scr.tipo_roteiro = script_type
                scr.descricao = description
                
                try:
                    # update Script
                    scr.save(user)
                except Exception, e:
                    self.log.error(u'Failed to update the Script.')
                    raise RoteiroError(e, u'Failed to update the Script.')
    
                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()
        
        except RoteiroNotFoundError:
            return self.response_error(165, id_script)  

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except RoteiroNameDuplicatedError:
            return self.response_error(250, script, script_type.tipo)
        
        except RoteiroError:
            return self.response_error(1)
        
    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Script.

        URL: script/<id_script>/
        """
        try:
            
            self.log.info("Remove Script")
            
            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            id_script = kwargs.get('id_script') 
            
            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)
            
            # Find Script by ID to check if it exist
            script = Roteiro.get_by_pk(id_script)
            
            with distributedlock(LOCK_SCRIPT % id_script):
                
                try:
                    
                    if script.equipamentoroteiro_set.count() != 0:
                        raise RoteiroHasEquipamentoError(None, u'Existe equipamento associado ao roteiro %s' % script.id)
                    
                    # remove Script
                    script.delete(user)
                    
                except RoteiroHasEquipamentoError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Script.')
                    raise RoteiroError(e, u'Failed to remove the Script.')
                
                return self.response(dumps_networkapi({}))
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroNotFoundError:
            return self.response_error(165, id_script)  

        except RoteiroHasEquipamentoError:
            return self.response_error(197, id_script)
        
        except RoteiroError:
            return self.response_error(1)