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

import datetime
import pecan

from oslo_config import cfg
from oslo_log import log
from pecan import rest

from shadowfiend.api import acl
from shadowfiend.api.controllers.v1 import models
from shadowfiend.common import exception
from shadowfiend.common import policy
from shadowfiend.common import timeutils
from shadowfiend.processor.service import fetcher
from shadowfiend.services import keystone as ks_client

from wsme import types as wtypes
from wsmeext.pecan import wsexpose


LOG = log.getLogger(__name__)
HOOK = pecan.request
CONF = cfg.CONF
CONF.import_opt('cloudkitty_period',
                'shadowfiend.processor.config',
                'processor')


class ExistAccountController(rest.RestController):
    """Manages operations on account."""

    _custom_actions = {
        'level': ['PUT'],
        'charges': ['GET'],
        'estimate': ['GET'],
    }

    def __init__(self, user_id):
        self._id = user_id

    def _account(self, user_id=None):
        _id = user_id or self._id
        try:
            account = HOOK.conductor_rpcapi.get_account(HOOK.context,
                                                        _id)
        except exception.AccountNotFound:
            LOG.error("Account %s not found" % _id)
            raise
        except exception.GetExternalBalanceFailed:
            raise
        except (Exception):
            LOG.error("Fail to get account %s" % _id)
            raise exception.AccountGetFailed(user_id=_id)
        return account

    @wsexpose(models.Charge, wtypes.text, body=models.Charge)
    def put(self, data):
        """Charge the account."""
        policy.check_policy(HOOK.context, "account:charge",
                            action="account:charge")

        # check accountant charge value
        lacv = int(CONF.limited_accountant_charge_value)
        if data.value > lacv:
            raise exception.InvalidChargeValue(value=data.value)
        try:
            charge = HOOK.conductor_rpcapi.charge_account(
                HOOK.context,
                self._id,
                **data.as_dict())

        except exception.NotAuthorized as e:
            LOG.error('Fail to charge the account:%s'
                      'due to not authorization' % self._id)
            raise exception.NotAuthorized()
        except Exception as e:
            LOG.error('Fail to charge the account:%s,'
                      'charge value: %s' % (self._id, data.value))
            raise exception.DBError(reason=e)
        return models.Charge.from_db_model(charge)

    @wsexpose(models.AdminAccount)
    def get(self):
        """Get this account."""
        policy.check_policy(HOOK.context, "account:get", action="account:get")
        user_id = self._id
        return models.AdminAccount(**self._account(user_id=user_id))

    @wsexpose(None)
    def delete(self):
        """Delete the account including the projects that belong to it."""
        policy.check_policy(HOOK.context, "account:delete",
                            action="account:delete")
        try:
            HOOK.conductor_rpcapi.delete_account(HOOK.context,
                                                 self._id)
        except exception.NotFound:
            LOG.Warning('Could not find account whose user_id is %s' %
                        self._id)
        except Exception as e:
            LOG.error('Fail to delete the account: %s' % self._id)
            raise exception.DBError(reason=e)

    @wsexpose(models.UserAccount, int)
    def level(self, level):
        """Update the account's level."""
        policy.check_policy(HOOK.context, "account:level",
                            action="account:level")

        if not isinstance(level, int) or level < 0 or level > 9:
            raise exception.InvalidParameterValue(err="Invalid Level")
        try:
            account = HOOK.conductor_rpcapi.change_account_level(
                HOOK.context, self._id, level)
        except Exception as e:
            LOG.error('Fail to change the account level of: %s' % self._id)
            raise exception.DBError(reason=e)

        return models.UserAccount(**account)

    @wsexpose(models.Charges, wtypes.text, datetime.datetime,
              datetime.datetime, int, int)
    def charges(self, type=None, start_time=None,
                end_time=None, limit=None, offset=None):
        """Get this account's charge records."""
        policy.check_policy(HOOK.context, "charges:get",
                            action="account:charges")

        if limit and limit < 0:
            raise exception.InvalidParameterValue(err="Invalid limit")
        if offset and offset < 0:
            raise exception.InvalidParameterValue(err="Invalid offset")

        user_id = acl.get_limited_to_user(
            HOOK.headers, 'account:charge') or self._id

        charges = HOOK.conductor_rpcapi.get_charges(HOOK.context,
                                                    user_id=user_id,
                                                    type=type,
                                                    limit=limit,
                                                    offset=offset,
                                                    start_time=start_time,
                                                    end_time=end_time)
        charges_list = []
        for charge in charges:
            charges_list.append(models.Charge(**charge))

        total_price, total_count = (HOOK.conductor_rpcapi.
                                    get_charges_price_and_count(
                                        HOOK.context,
                                        user_id=user_id,
                                        type=type,
                                        start_time=start_time,
                                        end_time=end_time))

        return models.Charges.transform(total_price=total_price,
                                        total_count=total_count,
                                        charges=charges_list)

    @wsexpose(models.Estimate)
    def estimate(self):
        """Get the price per day and the remaining days."""

        policy.check_policy(HOOK.context, "account:estimate",
                            action="account:estimate")
        _gnocchi_fetcher = fetcher.GnocchiFetcher()

        user_id = self._id
        account = self._account(user_id=user_id)
        price_per_hour = _gnocchi_fetcher.get_current_consume(
            HOOK.context.project_id)

        def _estimate(balance, price_per_hour, remaining_day):
            return models.Estimate(balance=round(balance, 2),
                                   price_per_hour=round(price_per_hour, 2),
                                   remaining_day=remaining_day)

        if price_per_hour == 0:
            if account['balance'] < 0:
                return _estimate(account['balance'], price_per_hour, -2)
            else:
                return _estimate(account['balance'], price_per_hour, -1)
        elif price_per_hour > 0:
            if account['balance'] < 0:
                return _estimate(account['balance'], price_per_hour, -2)
            else:
                price_per_day = price_per_hour * 24
                remaining_day = int(account['balance'] / price_per_day)
        return _estimate(account['balance'], price_per_hour, remaining_day)


class ChargesController(rest.RestController):

    @wsexpose(models.Charges, wtypes.text, wtypes.text,
              datetime.datetime, datetime.datetime, int, int,
              wtypes.text, wtypes.text)
    def get(self, user_id=None, type=None, start_time=None,
            end_time=None, limit=None, offset=None,
            sort_key='created_at', sort_dir='desc'):
        """Get all charges of all account."""

        policy.check_policy(HOOK.context, "charges:all",
                            action="charges:all")

        if limit and limit < 0:
            raise exception.InvalidParameterValue(err="Invalid limit")
        if offset and offset < 0:
            raise exception.InvalidParameterValue(err="Invalid offset")

        users = {}

        def _get_user(user_id):
            user = users.get(user_id)
            if user:
                return user
            contact = ks_client.get_user(user_id) or {}
            user_name = contact.get('name')
            email = contact.get('email')
            users[user_id] = models.User(user_id=user_id,
                                         user_name=user_name,
                                         email=email)
            return users[user_id]

        charges = HOOK.conductor_rpcapi.get_charges(
            HOOK.context,
            user_id=user_id,
            type=type,
            limit=limit,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            sort_key=sort_key,
            sort_dir=sort_dir)
        charges_list = []
        for charge in charges:
            acharge = models.Charge.from_db_model(charge)
            acharge.target = _get_user(charge['user_id'])
            charges_list.append(acharge)

        total_price, total_count = (HOOK.conductor_rpcapi.
                                    get_charges_price_and_count(
                                        HOOK.context,
                                        user_id=user_id,
                                        type=type,
                                        start_time=start_time,
                                        end_time=end_time))

        return models.Charges.transform(total_price=total_price,
                                        total_count=total_count,
                                        charges=charges_list)


class AccountController(rest.RestController):
    """Manages operations on account."""

    charges = ChargesController()

    @pecan.expose()
    def _lookup(self, user_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        _correct = len(user_id) == 32 or len(user_id) == 64
        if _correct:
            return ExistAccountController(user_id), remainder

    @wsexpose(None, body=models.AdminAccount, status_code=202)
    def post(self, data):
        """Create a new account."""
        policy.check_policy(HOOK.context,
                            "account:post",
                            action="account:post")
        try:
            account = data.as_dict()
            response = HOOK.conductor_rpcapi.create_account(HOOK.context,
                                                            account)
            return response
        except Exception as e:
            LOG.error('Fail to create account: %s' % data.as_dict())
            raise exception.DBError(reason=e)

    @wsexpose(models.AdminAccounts, bool, int, int, wtypes.text)
    def get_all(self, owed=None, limit=None, offset=None, duration=None):
        """Get this account."""
        policy.check_policy(HOOK.context, "account:all", action="account:all")
        owed = False

        if limit and limit < 0:
            raise exception.InvalidParameterValue(err="Invalid limit")
        if offset and offset < 0:
            raise exception.InvalidParameterValue(err="Invalid offset")

        duration = timeutils.normalize_timedelta(duration)
        if duration:
            active_from = timeutils.utcnow() - duration
        else:
            active_from = None

        try:
            accounts = HOOK.conductor_rpcapi.get_accounts(
                HOOK.context,
                owed=owed,
                limit=limit,
                offset=offset,
                active_from=active_from)
            count = len(accounts)
        except exception.NotAuthorized as e:
            LOG.error('Failed to get all accounts')
            raise exception.NotAuthorized()
        except Exception as e:
            LOG.error('Failed to get all accounts')
            raise exception.DBError(reason=e)

        accounts = [models.AdminAccount.transform(**account)
                    for account in accounts]

        return models.AdminAccounts.transform(total_count=count,
                                              accounts=accounts)
