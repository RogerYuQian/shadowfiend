# -*- coding: utf-8 -*-
# Copyright 2014 Objectif Libre
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
Time calculations functions

We're mostly using oslo_utils for time calculations but we're encapsulating it
to ease maintenance in case of library modifications.
"""

import calendar
import datetime
import iso8601
import sys
import time

from oslo_utils import timeutils
from six import moves
from stevedore import extension


# ISO 8601 extended time format with microseconds
_ISO8601_TIME_FORMAT_SUBSECOND = '%Y-%m-%dT%H:%M:%S.%f'
_ISO8601_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
PERFECT_TIME_FORMAT = _ISO8601_TIME_FORMAT_SUBSECOND


def parse_isotime(timestamp):
    """Parse time from ISO 8601 format."""
    try:
        return iso8601.parse_date(timestamp)
    except iso8601.ParseError as e:
        raise ValueError(e)
    except TypeError as e:
        raise ValueError(e)


def dt2ts(orig_dt):
    """Translate a datetime into a timestamp."""
    return calendar.timegm(orig_dt.timetuple())


def iso2dt(iso_date):
    """iso8601 format to datetime."""
    iso_dt = timeutils.parse_isotime(iso_date)
    trans_dt = timeutils.normalize_time(iso_dt)
    return trans_dt


def ts2dt(timestamp):
    """timestamp to datetime format."""
    if not isinstance(timestamp, float):
        timestamp = float(timestamp)
    return datetime.datetime.utcfromtimestamp(timestamp)


def ts2iso(timestamp):
    """timestamp to is8601 format."""
    if not isinstance(timestamp, float):
        timestamp = float(timestamp)
    return timeutils.iso8601_from_timestamp(timestamp)


def dt2iso(orig_dt):
    """datetime to is8601 format."""
    return timeutils.isotime(orig_dt)


def utcnow():
    """Returns a datetime for the current utc time."""
    return timeutils.utcnow()


def utcnow_ts():
    """Returns a timestamp for the current utc time."""
    return timeutils.utcnow_ts()


def nl2utc(timestamp):
    """Normalize time in arbitrary timezone to UTC naive object."""
    offset = timestamp.utcoffset()
    if offset is None:
        return timestamp
    return timestamp.replace(tzinfo=None) - offset


def str2ts(datetime):
    return time.mktime(
        time.strptime(datetime, _ISO8601_TIME_FORMAT))


def ts2str(timestamp):
    return time.strftime(_ISO8601_TIME_FORMAT, time.localtime(timestamp))


def strtime(at=None, fmt=PERFECT_TIME_FORMAT):
    """Returns formatted utcnow."""
    if not at:
        at = utcnow()
    return at.strftime(fmt)


def get_month_days(dt):
    return calendar.monthrange(dt.year, dt.month)[1]


def add_days(base_dt, days, stay_on_month=True):
    if stay_on_month:
        max_days = get_month_days(base_dt)
        if days > max_days:
            return get_month_end(base_dt)
    return base_dt + datetime.timedelta(days=days)


def add_month(dt, stay_on_month=True):
    next_month = get_next_month(dt)
    return add_days(next_month, dt.day, stay_on_month)


def get_month_start(dt=None):
    if not dt:
        dt = utcnow()
    month_start = datetime.datetime(dt.year, dt.month, 1)
    return month_start


def get_month_end(dt=None):
    month_start = get_month_start(dt)
    days_of_month = get_month_days(month_start)
    month_end = month_start.replace(day=days_of_month)
    return month_end


def get_next_month(dt=None):
    month_end = get_month_end(dt)
    next_month = month_end + datetime.timedelta(days=1)
    return next_month


def get_next_month_timestamp(dt=None):
    return dt2ts(get_next_month(dt))


def refresh_stevedore(namespace=None):
    """Trigger reload of entry points.

    Useful to have dynamic loading/unloading of stevedore modules.
    """
    # NOTE(sheeprine): pkg_resources doesn't support reload on python3 due to
    # defining basestring which is still there on reload hence executing
    # python2 related code.
    try:
        del sys.modules['pkg_resources'].basestring
    except AttributeError:
        # python2, do nothing
        pass
    # Force working_set reload
    moves.reload_module(sys.modules['pkg_resources'])
    # Clear stevedore cache
    cache = extension.ExtensionManager.ENTRY_POINT_CACHE
    if namespace:
        if namespace in cache:
            del cache[namespace]
    else:
        cache.clear()


def normalize_timedelta(duration):
    if not duration:
        return
    unit = duration[-1]
    value = duration[:-1]
    if unit == 'm':
        return datetime.timedelta(minutes=float(value))
    if unit == 'h':
        return datetime.timedelta(hours=float(value))
    if unit == 'd':
        return datetime.timedelta(days=float(value))
    raise ValueError("unsupport time unit")
