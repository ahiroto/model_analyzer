# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .mock_server import MockServerMethods
from .mock_api_error import MockAPIError
from unittest.mock import patch, Mock, MagicMock, call


class MockServerDockerMethods(MockServerMethods):
    """
    Mocks the docker module as used in
    model_analyzer/triton/server/server_docker.py. Provides functions to
    check operation.
    """

    TEST_LOG = "Triton Server Test Log"
    TEST_MEM = "10.0e3"

    def __init__(self):
        docker_container_attrs = {
            'exec_run':
            MagicMock(return_value=(None, bytes(self.TEST_MEM, 'utf-8'))),
            'stats':
            Mock(return_value={
                'memory_stats': {
                    'usage': 0.0,
                    'max_usage': 0.0,
                    'limits': 0.0
                }
            })
        }
        docker_client_attrs = {
            'containers.run': Mock(return_value=Mock(**docker_container_attrs))
        }
        docker_attrs = {
            'from_env': Mock(return_value=Mock(**docker_client_attrs)),
            'types.DeviceRequest': Mock(return_value=0)
        }
        self.patcher_docker = patch(
            'model_analyzer.triton.server.server_docker.docker',
            Mock(**docker_attrs))
        super().__init__()

    def start(self):
        """ 
        Start the patchers
        """

        self.mock = self.patcher_docker.start()

    def _fill_patchers(self):
        """
        Fill patcher list
        """

        self._patchers.append(self.patcher_docker)

    def _assert_docker_initialized(self):
        """
        Asserts that docker.from_env
        was called to initialize
        docker client
        """

        self.mock.from_env.assert_called()

    def _assert_docker_exec_run_with_args(self, cmd, stream):
        """
        Asserts that a command cmd was run on the docker container
        with the given stream value
        """

        self.mock.from_env.return_value.containers.run.return_value.exec_run.assert_any_call(
            cmd=cmd, stream=stream)

    def assert_server_process_start_called_with(self,
                                                cmd,
                                                model_repository_path,
                                                triton_image,
                                                http_port=8000,
                                                grpc_port=8001,
                                                metrics_port=8002):
        """
        Asserts that a triton container was created using the
        supplied arguments
        """

        self._assert_docker_initialized()

        mock_volumes = {
            model_repository_path: {
                'bind': model_repository_path,
                'mode': 'ro'
            }
        }
        mock_ports = {http_port: 8000, grpc_port: 8001, metrics_port: 8002}
        self.mock.from_env.return_value.containers.run.assert_called_once_with(
            command=cmd,
            name='tritonserver',
            image=triton_image,
            device_requests=[0],
            volumes=mock_volumes,
            ports=mock_ports,
            publish_all_ports=True,
            tty=False,
            stdin_open=False,
            detach=True)

    def raise_exception_on_container_run(self):
        """
        Raises MockAPIError on container run
        """
        self.exception_on_run_patcher = patch(
            'model_analyzer.triton.server.server_docker.docker.errors.APIError',
            MockAPIError)
        self.api_error_mock = self.exception_on_run_patcher.start()
        self.mock.from_env.return_value.containers.run.side_effect = \
            self.api_error_mock

    def stop_raise_exception_on_container_run(self):
        """
        Stop raising exception on container run
        """
        ...
        self.mock.from_env.return_value.containers.run.side_effect = None
        self.exception_on_run_patcher.stop()

    def assert_server_process_terminate_called(self):
        """
        Asserts that stop was called on the return value of containers.run
        """

        self.mock.from_env.return_value.containers.run.return_value.stop.assert_called(
        )
        self.mock.from_env.return_value.containers.run.return_value.remove.assert_called(
        )

    def assert_cpu_stats_called(self):
        """
        Checks the call to docker.Container.stats
        """

        self._assert_docker_exec_run_with_args(
            cmd=
            'bash -c "pmap -x $(pgrep tritonserver) | tail -n1 | awk \'{print $4}\'"',
            stream=False)
        self._assert_docker_exec_run_with_args(
            cmd='bash -c "free | awk \'{if(NR==2)print $7}\'"', stream=False)
