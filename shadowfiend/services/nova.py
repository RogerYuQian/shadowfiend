# -*- coding: utf-8 -*-
# Copyright 2017 Openstack Foundation.
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

from keystoneauth1 import loading as ks_loading
from novaclient import client as nova_client
from novaclient.exceptions import NotFound

from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)
CONF = cfg.CONF


def drop_resource(service, resource_id):
    _nova_client = NovaClient()
    if service == 'compute':
        _nova_client.delete_server(resource_id)


class NovaClient(object):
    def __init__(self):
        ks_loading.register_session_conf_options(CONF, "nova_client")
        ks_loading.register_auth_conf_options(CONF, "nova_client")
        self.auth = ks_loading.load_auth_from_conf_options(
            CONF,
            "nova_client")
        self.session = ks_loading.load_session_from_conf_options(
            CONF,
            "nova_client",
            auth=self.auth)
        self.nova_client = nova_client.Client(
            version='2',
            session=self.session,
            auth_url=self.auth.auth_url)

    def delete_server(self, instance_id):
        try:
            self.nova_client.servers.delete(instance_id)
        except NotFound:
            return None
        return True
