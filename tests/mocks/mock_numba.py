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

from unittest.mock import patch, MagicMock, Mock

from .mock_dcgm_agent import TEST_PCI_BUS_ID
from .mock_base import MockBase


class MockNumba(MockBase):
    """
    Mocks numba class
    """
    def __init__(self, mock_paths):
        device = MagicMock()

        # Ignore everything after 0
        test_pci_id = str(TEST_PCI_BUS_ID, encoding='ascii').split('.')[0]

        pci_domain_id, pci_bus_id, pci_device_id = test_pci_id.split(':')
        device.get_device_identity = MagicMock(
            return_value={
                'pci_bus_id': int(pci_bus_id, 16),
                'pci_domain_id': int(pci_domain_id, 16),
                'pci_device_id': int(pci_device_id, 16)
            })
        device.id = 0
        list_devices = MagicMock()
        list_devices.return_value = [device]

        cuda_attrs = {'list_devices': list_devices}
        numba_attrs = {'cuda': MagicMock(**cuda_attrs)}
        self._mock_paths = mock_paths
        self._patchers_numba = {}
        self._numba_mocks = {}

        for path in mock_paths:
            self._patchers_numba[path] = patch(f"{path}.numba",
                                               Mock(**numba_attrs))
        super().__init__()

    def _fill_patchers(self):
        """
        Fills the patcher list for destruction
        """

        for patcher in self._patchers_numba.values():
            self._patchers.append(patcher)
