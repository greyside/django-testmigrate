# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_failure', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(lambda apps, schema_editor: None, lambda apps, schema_editor: None),
    ]
    
    def test_unapply_success(self, apps, testcase):
        testcase.assertFalse(True)
