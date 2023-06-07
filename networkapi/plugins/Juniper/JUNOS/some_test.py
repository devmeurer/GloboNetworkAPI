from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.base import BasePlugin
from networkapi.plugins import exceptions
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS
from mock import patch, MagicMock
from jnpr.junos.exception import RPCError, RpcError, LockError, ConfigLoadError, CommitError

from jnpr.junos.device import logger as device_logger
from ncclient.transport.ssh import logger as ssh_logger
from ncclient.transport.session import logger as session_logger
from ncclient.operations.rpc import logger as rpc_logger

class JunosPluginTest(NetworkApiTestCase):

    """
    Junos plugin tests

    How to use:
        cd GloboNetworkAPI
        docker exec -it netapi_app ./fast_start_test_reusedb.sh networkapi/plugins/Juniper/JUNOS/tests.py

    General notes:
        - autospec=True: responds to methods that actually exist in the real class
        - assert_called_once_with() assert if an important step was called
    """

    @patch('networkapi.equipamento.models.EquipamentoAcesso', autospec=True)
    def setUp(self, mock_equipment_access):
        
        """
        Equipment mock is a fake class used in specific test cases below
        """

        mock_equipment_access.fqdn = 'any fqdn'
        mock_equipment_access.user = 'any user'
        mock_equipment_access.password = 'any password'
        self.mock_equipment_access = mock_equipment_access

    def test_create_junos_with_super_class(self):

        """
        test_create_junos_with_super_class - test if Junos plugin is the BasePlugin
        """

        plugin = JUNOS()
        self.assertIsInstance(plugin, BasePlugin)

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.Device', autospec=True)
    def test_connect_success(self, mock_device):

        """
        test_connect_success - Simulate connect success using Junos Device mock.

        Note: All internal functions in Device Class are mocked, raising no exceptions on it

        Warning: For an unknown reason was not possible to use
        'jnpr.junos.Device' instead 'networkapi.plugins.Juniper.JUNOS.plugin.Device'
        """

        # Mocking result
        mock_device.return_value.connected = True

        # Close real test
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        connection_response = plugin.connect()

        # Asserts
        plugin.remote_conn.open.assert_called_with()
        self.assertIsNotNone(plugin.configuration)
        self.assertEqual(connection_response, True)

    def test_connect_wrong_data_exception(self):

        """
        test_connect_wrong_data_exception
        """

        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        with self.assertRaises(exceptions.ConnectionException):
            plugin.connect()

    @patch('jnpr.junos.utils.config.Config')
    def test_exec_command_success(self, mock_config):

        """
        test_exec_command_success - This test asserts the success of the complete workflow of executing any command.
        Note: All internal functions in Config Class are mocked, raising no exceptions on it
        """

        # Mocking result
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.plugin_try_lock = MagicMock()
        plugin.plugin_try_lock.return_value = True
        plugin.configuration = mock_config

        # Close real test
        exec_command_response = plugin.exec_command("any command")

        # Assert
        plugin.configuration.rollback.assert_called_once()
        plugin.configuration.load.assert_called_once()
        plugin.configuration.commit_check.assert_called_once()
        plugin.configuration.commit.assert_called_once()
        plugin.configuration.unlock.assert_called_once()
        self.assertIsNotNone(exec_command_response)

    @patch('jnpr.junos.utils.config.Config')
    @patch('time.sleep')
    def test_exec_command_fail_to_lock(self, time_sleep, mock_config):

        """
        test_exec_command_fail_to_lock
        """

        # Mocks
        time_sleep.return_value = None  # to be executed instantly
        mock_config.lock.side_effect = LockError('')  # Forced exception here

        # Create plugin
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.configuration = mock_config  # add mock to plugin instance

        # Test
        with self.assertRaises(exceptions.APIException):
            plugin.exec_command("any command")
        plugin.configuration.lock.assert_called_with()

    @patch('jnpr.junos.utils.config.Config')
    @patch('jnpr.junos.exception.RpcError')
    def test_exec_command_fail_to_load(self, mock_rpc_error, mock_config):

        # Mocks
        config_load_error = ConfigLoadError('')
        config_load_error.rpc_error = mock_rpc_error
        mock_config.load.side_effect = config_load_error  # Forced exception here

        # Create plugin
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.configuration = mock_config  # add mock to plugin instance

        # Test
        with self.assertRaises(exceptions.APIException):
            plugin.exec_command("any command")
        plugin.configuration.load.assert_called_with(
            "any command", format='set', ignore_warning=plugin.ignore_warning_list)

    @patch('jnpr.junos.utils.config.Config')
    def test_exec_command_fail_to_commit_check(self, mock_config):

        # Mocks
        error = RpcError('')
        mock_config.commit_check.side_effect = error  # Forced exception here

        # Create plugin
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.configuration = mock_config  # add mock to plugin instance

        # Tests
        with self.assertRaises(exceptions.APIException):
            plugin.exec_command("any command")
        plugin.configuration.commit_check.assert_called_with()

    @patch('jnpr.junos.utils.config.Config')
    @patch('jnpr.junos.exception.RpcError')
    def test_exec_command_fail_to_commit_check(self, mock_rpc_error, mock_config):

        # Mocks
        error = CommitError('')
        error.rpc_error = mock_rpc_error
        mock_config.commit.side_effect = error  # Forced exception here

        # Create plugin
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.configuration = mock_config  # add mock to plugin instance

        # Tests
        with self.assertRaises(exceptions.APIException):
            plugin.exec_command("any command")
        plugin.configuration.commit.assert_called_with()

    @patch('jnpr.junos.Device')
    def test_call_close_success(self, mock_device):

        """
        test_call_close_success - Test if the plugin junos plugin close a connection with the expected asserts
        """

        # Mocking
        mock_device.connected = False
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.remote_conn = mock_device

        # Close to a real test:
        close_response = plugin.close()

        # Asserts
        plugin.remote_conn.close.assert_called_once_with()
        self.assertTrue(close_response, True)

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_copyScriptFileToConfig(self, mock_junos_plugin):
        mock_junos_plugin.copyScriptFileToConfig("any file path")
        mock_junos_plugin.copyScriptFileToConfig.assert_called_with("any file path")

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.StartShell')
    def test_call_ensure_privilege_level_success(self, mock_start_shell):

        """
        test_call_ensure_privilege_level_success

        Note: The shell run function expects an array as a return value,
        and ensure_privilege_level() parse it to ensure the privilege.
        """

        mock_start_shell.return_value.run.return_value = [
            False,
            'cli -c "show cli authorization"\r\r\nCurrent user: \'root        \' class \'super-user\'\r']

        plugin = JUNOS(equipment_access=self.mock_equipment_access)

        # Mock connection
        plugin.remote_conn = MagicMock()
        plugin.remote_conn.connected.return_value = True

        result = plugin.ensure_privilege_level()
        self.assertTrue(result)

    def test_call_ensure_privilege_level_fail(self):
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        with self.assertRaises(Exception):
            plugin.ensure_privilege_level()

    @patch('os.path.isfile')
    @patch('networkapi.plugins.Juniper.JUNOS.plugin.get_value')
    def test_check_configuration_file_exists_from_system_variable(self, mock_get_value, mock_is_file):
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        mock_get_value.return_value = "/any_base_variable_path/"
        mock_is_file.return_value = True

        # isfile.return_value = True
        result = plugin.check_configuration_file_exists("any_configuration_path_with_file_name")
        self.assertEqual(result, "/any_base_variable_path/any_configuration_path_with_file_name")

    @patch('os.path.isfile')
    def test_check_configuration_file_exists_from_static_variable(self, mock_is_file):
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        mock_is_file.return_value = True
        first_alternative_static_base_path = plugin.alternative_static_base_path_list[0]

        result = plugin.check_configuration_file_exists("any_configuration_path_with_file_name")
        self.assertEqual(result, first_alternative_static_base_path+"any_configuration_path_with_file_name")

    @patch('os.path.isfile')
    def test_check_configuration_file_exists_from_relative_path(self, mock_is_file):
        plugin = JUNOS(equipment_access=self.mock_equipment_access)

        # The function is_file(...), inside check_configuration_file_exists, is used two times.
        # The proposed test need that function is_file(...) returns two different values at different places.
        # Returning True at first and False at second time, where the principal test is executed
        mock_is_file.side_effect = [False, True]

        result = plugin.check_configuration_file_exists("any_configuration_path_with_file_name")
        self.assertEqual(result, "any_configuration_path_with_file_name")  # Must be the same

    def test_set_detailed_junos_log_level_not_defined_at_db(self):

        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        loggers = [device_logger, ssh_logger, session_logger, rpc_logger]
        result = plugin.set_detailed_junos_log_level(loggers)
        self.assertEqual(result, 'ERROR')

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.get_value')
    def test_set_detailed_junos_log_level_defined_at_db(self, mock_get_value):

        mock_get_value.return_value = 'WARNING'

        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        loggers = [device_logger, ssh_logger, session_logger, rpc_logger]
        result = plugin.set_detailed_junos_log_level(loggers)

        self.assertEqual(result, 'WARNING')

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.get_value')
    def test_set_detailed_junos_log_level_defined_wrong_at_db(self, mock_get_value):

        mock_get_value.return_value = 'WRONG'

        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        loggers = [device_logger, ssh_logger, session_logger, rpc_logger]
        result = plugin.set_detailed_junos_log_level(loggers)

        self.assertEqual(result, 'ERROR')
