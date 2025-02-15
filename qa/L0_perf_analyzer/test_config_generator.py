# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
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

import yaml


class TestConfigGenerator:
    """
    This class contains functions that
    create configs for various test scenarios.
    
    The `setup` function does the work common to all tests

    TO ADD A TEST: Simply add a member function whose name starts
                    with 'generate'.
    """

    def __init__(self):
        test_functions = [
            self.__getattribute__(name)
            for name in dir(self)
            if name.startswith('generate')
        ]

        for test_function in test_functions:
            self.setup()
            test_function()

    def setup(self):
        pass

    def generate_time_window_5000(self):
        model_config = {
            'analysis_models': ['vgg19_libtorch'],
            'profile_models': ['vgg19_libtorch'],
            'perf_analyzer_flags': {
                'measurement-mode': 'time_windows',
                'measurement-interval': 5000
            }
        }
        with open('./config-time-window-5000.yml', 'w') as f:
            yaml.dump(model_config, f)

    def generate_time_window_50(self):
        model_config = {
            'analysis_models': ['vgg19_libtorch'],
            'profile_models': ['vgg19_libtorch'],
            'perf_analyzer_flags': {
                'measurement-mode': 'time_windows',
                'measurement-interval': 50
            }
        }
        with open('./config-time-window-50.yml', 'w') as f:
            yaml.dump(model_config, f)


if __name__ == '__main__':
    TestConfigGenerator()
