# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_prod_config 1'] = '''{
  "DEBUG": false,
  "SQLALCHEMY_DATABASE_URI": "the-db-url",
  "SQLALCHEMY_TRACK_MODIFICATIONS": false
}'''
