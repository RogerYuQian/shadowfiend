# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from shadowfiend.tests.unit.api import base as api_base


class TestRoot(api_base.FunctionalTest):

    def test_get_root(self):
        response = self.get_json('/', path_prefix='')
        # Check fields are not empty
        [self.assertNotIn(f, ['', []]) for f in response]

        self.assertEqual('v1', response['versions'][0]['id'])
