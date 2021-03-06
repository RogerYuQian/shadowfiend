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

import logging

from shadowfiend.client import client


LOG = logging.getLogger(__name__)
TIMESTAMP_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class Client(object):
    """Client for shadowfiend v1 API

    """
    def __init__(self, auth_plugin="token",
                 verify=True, cert=None, timeout=None, *args, **kwargs):
        self.client = client.Client(auth_plugin=auth_plugin,
                                    verify=verify,
                                    cert=cert,
                                    timeout=timeout,
                                    *args, **kwargs)

    def get_billing_owner(self, project_id):
        resp, body = self.client.get('/projects/%s/billing_owner' %
                                     project_id)
        return body

    def create_project(self, user_id, project_id, domain_id, consumption):
        _body = dict(user_id=user_id,
                     project_id=project_id,
                     domain_id=domain_id,
                     consumption=consumption)
        self.client.post('/projects', body=_body)

    def get_project(self, project_id):
        resp, body = self.client.get('/projects/%s' % project_id)
        return body

    def get_projects(self, user_id=None, type=None, duration=None):
        _body = dict(user_id=user_id,
                     type=type,
                     duration=duration)
        resp, body = self.client.get('/projects', body=_body)
        return body

    def get_account(self, user_id):
        resp, body = self.client.get('/accounts/%s' % user_id)
        return body

    def get_accounts(self, owed=None, limit=None, offset=None, duration=None):
        _body = dict(owed=owed,
                     limit=limit,
                     offset=offset,
                     duration=duration)
        resp, body = self.client.get('/accounts', body=_body)
        return body

    def create_account(self, user_id, domain_id, balance,
                       consumption, level, **kwargs):
        _body = dict(user_id=user_id,
                     domain_id=domain_id,
                     balance=balance,
                     consumption=consumption,
                     level=level,
                     **kwargs)
        self.client.post('/accounts', body=_body)

    def delete_account(self, user_id):
        resp, body = self.client.delete('/accounts/%s' % user_id)
        return body

    def change_account_level(self, user_id, level):
        _body = dict(level=level)
        self.client.put('/accounts/%s/level' % user_id, body=_body)

    def update_account(self, **kwargs):
        user_id = kwargs.pop('user_id')
        self.client.put('/accounts/%s' % user_id, body=kwargs)

    def get_charges(self, user_id):
        resp, body = self.client.get('/accounts/%s/charges' % user_id)
        if body:
            return body['charges']
        return []
