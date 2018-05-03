# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-03 17:50
from __future__ import unicode_literals

from django.db import migrations

CREATE_NODE_PROVIDER_PARTIAL_INDEX = """
    CREATE UNIQUE INDEX preprint_node_provider_index
    ON osf_preprint (node_id, provider_id)
    WHERE node_id IS NOT NULL;
"""

DROP_NODE_PROVIDER_PARTIAL_INDEX = """
    DROP INDEX preprint_node_provider_index
"""


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0095_update_preprint_model_for_divorce'),
    ]

    operations = [
        migrations.RunSQL(CREATE_NODE_PROVIDER_PARTIAL_INDEX, DROP_NODE_PROVIDER_PARTIAL_INDEX)
    ]
