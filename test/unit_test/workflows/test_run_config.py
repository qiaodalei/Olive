# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from olive.workflows.run.config import RunConfig


class TestRunConfig:
    # TODO: add more tests for different config files to test olive features
    # like: Systems/Evaluation/Model and etc.
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_script_config_file = Path(__file__).parent / "mock_data" / "user_script.json"

    @pytest.mark.parametrize(
        "config_file",
        [
            Path(__file__).parent / "mock_data" / "transformer_dataset.json",
            Path(__file__).parent / "mock_data" / "only_transformer_dataset.json",
            Path(__file__).parent / "mock_data" / "ner_task_dataset.json",
        ],
    )
    def test_dataset_config_file(self, config_file):
        run_config = RunConfig.parse_file(config_file)
        for dc in run_config.data_configs.values():
            dc.to_data_container().create_dataloader()

    @pytest.mark.parametrize("system", ["local_system", "azureml_system"])
    def test_user_script_config(self, system):
        with open(self.user_script_config_file, "r") as f:
            user_script_config = json.load(f)

        user_script_config["engine"]["host"] = system
        user_script_config["engine"]["target"] = system
        config = RunConfig.parse_obj(user_script_config)
        for metric in config.evaluators["common_evaluator"].metrics:
            assert metric.user_config.data_dir.get_path().startswith("azureml://")

    def test_config_without_azureml_config(self):
        with open(self.user_script_config_file, "r") as f:
            user_script_config = json.load(f)

        user_script_config.pop("azureml_client")
        with pytest.raises(ValueError) as e:
            RunConfig.parse_obj(user_script_config)
            assert str(e.value) == "AzureML client config is required for AzureML system"

    @pytest.fixture
    def mock_aml_credentials(self):
        # we need to mock all the credentials because the default credential will get tokens from all of them
        self.mocked_env_credentials = patch("azure.identity._credentials.default.EnvironmentCredential").start()
        self.mocked_managed_identity_credentials = patch(
            "azure.identity._credentials.default.ManagedIdentityCredential"
        ).start()
        self.mocked_shared_token_cache_credentials = patch(
            "azure.identity._credentials.default.SharedTokenCacheCredential"
        ).start()
        self.mocked_azure_cli_credentials = patch("azure.identity._credentials.default.AzureCliCredential").start()
        self.mocked_azure_powershell_credentials = patch(
            "azure.identity._credentials.default.AzurePowerShellCredential"
        ).start()
        self.mocked_interactive_browser_credentials = patch(
            "azure.identity._credentials.default.InteractiveBrowserCredential"
        ).start()
        yield
        patch.stopall()

    @pytest.mark.usefixtures("mock_aml_credentials")
    @pytest.mark.parametrize(
        "default_auth_params",
        [
            (None, (1, 1, 1, 1, 1, 0)),
            (
                {"exclude_environment_credential": True, "exclude_managed_identity_credential": False},
                (0, 1, 1, 1, 1, 0),
            ),
            ({"exclude_environment_credential": True, "exclude_managed_identity_credential": True}, (0, 0, 1, 1, 1, 0)),
        ],
    )
    def test_config_with_azureml_default_auth_params(self, default_auth_params):
        """
        default_auth_params[0] is a dict of the parameters to be passed to DefaultAzureCredential

        default_auth_params[1] is a tuple of the number of times each credential is called.
        the order is totally same with that in DefaultAzureCredential where the credentials
        are called sequentially until one of them succeeds:
            EnvironmentCredential -> ManagedIdentityCredential -> SharedTokenCacheCredential
            -> AzureCliCredential -> AzurePowerShellCredential -> InteractiveBrowserCredential
        https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python # noqa: E501
        """
        with open(self.user_script_config_file, "r") as f:
            user_script_config = json.load(f)

        user_script_config["azureml_client"]["default_auth_params"] = default_auth_params[0]
        config = RunConfig.parse_obj(user_script_config)
        config.azureml_client.create_client()
        assert (
            self.mocked_env_credentials.call_count,
            self.mocked_managed_identity_credentials.call_count,
            self.mocked_shared_token_cache_credentials.call_count,
            self.mocked_azure_cli_credentials.call_count,
            self.mocked_azure_powershell_credentials.call_count,
            self.mocked_interactive_browser_credentials.call_count,
        ) == default_auth_params[1]

    @patch("azure.identity.DefaultAzureCredential")
    @patch("azure.identity.InteractiveBrowserCredential")
    def test_config_with_failed_azureml_default_auth(self, mocked_interactive_login, mocked_default_azure_credential):
        mocked_default_azure_credential.side_effect = Exception("mock error")
        with open(self.user_script_config_file, "r") as f:
            user_script_config = json.load(f)
        config = RunConfig.parse_obj(user_script_config)
        config.azureml_client.create_client()
        assert mocked_interactive_login.call_count == 1

    def test_readymade_system(self):
        readymade_config_file = Path(__file__).parent / "mock_data" / "readymade_system.json"
        with open(readymade_config_file, "r") as f:
            user_script_config = json.load(f)

        cfg = RunConfig.parse_obj(user_script_config)
        assert cfg.engine.target.config.accelerators == ["GPU"]
