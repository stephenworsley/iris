# (C) British Crown Copyright 2013 - 2019, Met Office
#
# This file is part of Iris.
#
# Iris is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Iris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Iris.  If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for the `iris.time.PartialDateTime` class."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six

# Import iris.tests first so that some things can be initialised before
# importing anything else.
import iris.tests as tests

import datetime
import operator
from unittest import mock

import cftime

from iris.time import PartialDateTime


class Test___init__(tests.IrisTest):
    def test_positional(self):
        # Test that we can define PartialDateTimes with positional arguments.
        pd = PartialDateTime(1066, None, 10)
        self.assertEqual(pd.year, 1066)
        self.assertEqual(pd.month, None)
        self.assertEqual(pd.day, 10)

    def test_keyword_args(self):
        # Test that we can define PartialDateTimes with keyword arguments.
        pd = PartialDateTime(microsecond=10)
        self.assertEqual(pd.year, None)
        self.assertEqual(pd.microsecond, 10)


class Test___repr__(tests.IrisTest):
    def test_full(self):
        pd = PartialDateTime(*list(range(7)))
        result = repr(pd)
        self.assertEqual(result, 'PartialDateTime(year=0, month=1, day=2,'
                                 ' hour=3, minute=4, second=5,'
                                 ' microsecond=6)')

    def test_partial(self):
        pd = PartialDateTime(month=2, day=30)
        result = repr(pd)
        self.assertEqual(result, 'PartialDateTime(month=2, day=30)')

    def test_empty(self):
        pd = PartialDateTime()
        result = repr(pd)
        self.assertEqual(result, 'PartialDateTime()')


class Test_timetuple(tests.IrisTest):
    def test_exists(self):
        # Check that the PartialDateTime class implements a timetuple (needed
        # because of http://bugs.python.org/issue8005).
        pd = PartialDateTime(*list(range(7)))
        self.assertTrue(hasattr(pd, 'timetuple'))


class _Test_operator(object):
    def test_invalid_type(self):
        pdt = PartialDateTime()
        with self.assertRaises(TypeError):
            self.op(pdt, 1)

    def _test(self, pdt, other, name):
        expected = self.expected_value[name]
        if isinstance(expected, type):
            with self.assertRaises(expected):
                result = self.op(pdt, other)
        else:
            result = self.op(pdt, other)
            self.assertIs(result, expected)

    def _test_dt(self, pdt, name):
        other = mock.Mock(name='datetime', spec=datetime.datetime,
                          year=2013, month=3, day=20, second=2)
        self._test(pdt, other, name)

    def test_no_difference(self):
        self._test_dt(PartialDateTime(year=2013, month=3, day=20, second=2),
                      'no_difference')

    def test_null(self):
        self._test_dt(PartialDateTime(), 'null')

    def test_item1_lo(self):
        self._test_dt(PartialDateTime(year=2011, month=3, second=2),
                      'item1_lo')

    def test_item1_hi(self):
        self._test_dt(PartialDateTime(year=2015, month=3, day=24), 'item1_hi')

    def test_item2_lo(self):
        self._test_dt(PartialDateTime(year=2013, month=1, second=2),
                      'item2_lo')

    def test_item2_hi(self):
        self._test_dt(PartialDateTime(year=2013, month=5, day=24), 'item2_hi')

    def test_item3_lo(self):
        self._test_dt(PartialDateTime(year=2013, month=3, second=1),
                      'item3_lo')

    def test_item3_hi(self):
        self._test_dt(PartialDateTime(year=2013, month=3, second=42),
                      'item3_hi')

    def test_mix_hi_lo(self):
        self._test_dt(PartialDateTime(year=2015, month=1, day=24), 'mix_hi_lo')

    def test_mix_lo_hi(self):
        self._test_dt(PartialDateTime(year=2011, month=5, day=24), 'mix_lo_hi')

    def _test_pdt(self, other, name):
        pdt = PartialDateTime(year=2013, day=24)
        self._test(pdt, other, name)

    def test_pdt_same(self):
        self._test_pdt(PartialDateTime(year=2013, day=24), 'pdt_same')

    def test_pdt_diff(self):
        self._test_pdt(PartialDateTime(year=2013, day=25), 'pdt_diff')

    def test_pdt_diff_fewer_fields(self):
        self._test_pdt(PartialDateTime(year=2013), 'pdt_diff_fewer')

    def test_pdt_diff_more_fields(self):
        self._test_pdt(PartialDateTime(year=2013, day=24, hour=12),
                       'pdt_diff_more')

    def test_pdt_diff_no_fields(self):
        pdt1 = PartialDateTime()
        pdt2 = PartialDateTime(month=3, day=24)
        self._test(pdt1, pdt2, 'pdt_empty')


def negate_expectations(expectations):
    def negate(expected):
        if not isinstance(expected, type):
            expected = not expected
        return expected

    return {name: negate(value) for name, value in six.iteritems(expectations)}


EQ_EXPECTATIONS = {'no_difference': True, 'item1_lo': False, 'item1_hi': False,
                   'item2_lo': False, 'item2_hi': False, 'item3_lo': False,
                   'item3_hi': False, 'mix_hi_lo': False, 'mix_lo_hi': False,
                   'null': True, 'pdt_same': True, 'pdt_diff': False,
                   'pdt_diff_fewer': False, 'pdt_diff_more': False,
                   'pdt_empty': False}

GT_EXPECTATIONS = {'no_difference': False, 'item1_lo': False, 'item1_hi': True,
                   'item2_lo': False, 'item2_hi': True, 'item3_lo': False,
                   'item3_hi': True, 'mix_hi_lo': True, 'mix_lo_hi': False,
                   'null': False, 'pdt_same': TypeError, 'pdt_diff': TypeError,
                   'pdt_diff_fewer': TypeError, 'pdt_diff_more': TypeError,
                   'pdt_empty': TypeError}

LT_EXPECTATIONS = {'no_difference': False, 'item1_lo': True, 'item1_hi': False,
                   'item2_lo': True, 'item2_hi': False, 'item3_lo': True,
                   'item3_hi': False, 'mix_hi_lo': False, 'mix_lo_hi': True,
                   'null': False, 'pdt_same': TypeError, 'pdt_diff': TypeError,
                   'pdt_diff_fewer': TypeError, 'pdt_diff_more': TypeError,
                   'pdt_empty': TypeError}


class Test___eq__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.eq
        self.expected_value = EQ_EXPECTATIONS

    def test_cftime_equal(self):
        pdt = PartialDateTime(month=3, microsecond=2)
        other = cftime.datetime(year=2013, month=3, day=20, second=2)
        self.assertTrue(pdt == other)

    def test_cftime_not_equal(self):
        pdt = PartialDateTime(month=3, microsecond=2)
        other = cftime.datetime(year=2013, month=4, day=20, second=2)
        self.assertFalse(pdt == other)


class Test___ne__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.ne
        self.expected_value = negate_expectations(EQ_EXPECTATIONS)


class Test___gt__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.gt
        self.expected_value = GT_EXPECTATIONS

    def test_cftime_greater(self):
        pdt = PartialDateTime(month=3, microsecond=2)
        other = cftime.datetime(year=2013, month=2, day=20, second=3)
        self.assertTrue(pdt > other)

    def test_cftime_not_greater(self):
        pdt = PartialDateTime(month=3, microsecond=2)
        other = cftime.datetime(year=2013, month=3, day=20, second=3)
        self.assertFalse(pdt > other)


class Test___le__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.le
        self.expected_value = negate_expectations(GT_EXPECTATIONS)


class Test___lt__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.lt
        self.expected_value = LT_EXPECTATIONS


class Test___ge__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.ge
        self.expected_value = negate_expectations(LT_EXPECTATIONS)


class Test___le__(tests.IrisTest, _Test_operator):
    def setUp(self):
        self.op = operator.le
        self.expected_value = negate_expectations(GT_EXPECTATIONS)


if __name__ == "__main__":
    tests.main()
