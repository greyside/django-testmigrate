# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_data(apps, schema_editor):
    MyModel = apps.get_model("test_success_reverse_halted", "MyModel")
    
    MyModel.objects.update(text='foo')


class Migration(migrations.Migration):

    dependencies = [
        ('test_success_reverse_halted', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            populate_data,
        ),
    ]
    
    def test_apply_start(self, apps, testcase):
        testcase.assertTrue(True)
    
    def test_apply_success(self, apps, testcase):
        testcase.assertTrue(True)
    
    def test_unapply_start(self, apps, testcase):
        testcase.assertTrue(True)
