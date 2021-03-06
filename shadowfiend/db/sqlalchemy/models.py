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

"""
SQLAlchemy models for Shadowfiend data
"""

import urlparse

from oslo_config import cfg
from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime, DECIMAL, Boolean
from sqlalchemy.ext.declarative import declarative_base

from shadowfiend.common import timeutils


def table_args():
    engine_name = urlparse.urlparse(cfg.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class ShadowfiendBase(object):
    """Base class for Shadowfiend Models."""
    __table_args__ = table_args()
    __table_initialized__ = False

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in values.iteritems():
            setattr(self, k, v)


Base = declarative_base(cls=ShadowfiendBase)


class Account(Base):

    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    domain_id = Column(String(255))
    balance = Column(DECIMAL(20, 4))
    consumption = Column(DECIMAL(20, 4))
    level = Column(Integer)
    owed = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)

    owed_at = Column(DateTime)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)


class Project(Base):

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    project_id = Column(String(255))
    consumption = Column(DECIMAL(20, 4))
    domain_id = Column(String(255))

    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow)


class UsrPrjRelation(Base):

    __tablename__ = 'usr_prj_relation'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    project_id = Column(String(255))
    consumption = Column(DECIMAL(20, 4))
    domain_id = Column(String(255))

    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow)


class Charge(Base):

    __tablename__ = 'charge'

    id = Column(Integer, primary_key=True)
    charge_id = Column(String(255))
    user_id = Column(String(255))
    domain_id = Column(String(255))
    value = Column(DECIMAL(20, 4))
    type = Column(String(64))
    come_from = Column(String(255))
    charge_time = Column(DateTime)
    trading_number = Column(String(255))
    operator = Column(String(64))
    remarks = Column(String(255))

    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime)
