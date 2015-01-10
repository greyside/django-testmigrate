# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_data(apps, schema_editor):
    MyModel = apps.get_model("test_failure", "MyModel")
    
    MyModel.objects.update(text='foo')


def populate_data_rev(apps, schema_editor):
    MyModel = apps.get_model("test_failure", "MyModel")
    
    MyModel.objects.update(text='')


class Migration(migrations.Migration):

    dependencies = [
        ('test_failure', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            populate_data,
            populate_data_rev,
        ),
    ]
    
    def test_apply_start(self, apps, testcase):
        testcase.assertFalse(True)
    
    def test_apply_success(self, apps, testcase):
        testcase.assertTrue(True)
    
    def test_unapply_start(self, apps, testcase):
        testcase.assertTrue(True)
    
    def test_unapply_success(self, apps, testcase):
        testcase.assertTrue(True)
