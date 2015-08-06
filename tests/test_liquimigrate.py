#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_liquimigrate
----------------------------------

Tests for `liquimigrate` module.
"""

from datetime import datetime, timedelta
import os
import unittest

import liquimigrate


class TestLiquimigrate(unittest.TestCase):

    def test_empty(self):
        self.assertTrue(True)
