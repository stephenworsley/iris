# Copyright Iris contributors
#
# This file is part of Iris and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Unit tests for
:func:`iris.fileformats.pp_load_rules._convert_scalar_realization_coords`.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

# Import iris.tests first so that some things can be initialised before
# importing anything else.
import iris.tests as tests

from iris.coords import DimCoord
from iris.tests.unit.fileformats import TestField

from iris.fileformats.pp_load_rules import _convert_scalar_realization_coords


class Test(TestField):
    def test_valid(self):
        coords_and_dims = _convert_scalar_realization_coords(lbrsvd4=21)
        self.assertEqual(coords_and_dims,
                         [(DimCoord([21], standard_name='realization'), None)])

    def test_missing_indicator(self):
        coords_and_dims = _convert_scalar_realization_coords(lbrsvd4=0)
        self.assertEqual(coords_and_dims, [])


if __name__ == "__main__":
    tests.main()
