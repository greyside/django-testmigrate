# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_data(apps, schema_editor):
    MyModel = apps.get_model("test_success_reverse_halted", "MyModel")
    
    MyModel.objects.update(text='bar')


def populate_data_rev(apps, schema_editor):
    MyModel = apps.get_model("test_success_reverse_halted", "MyModel")
    
    MyModel.objects.update(text='foo')


class Migration(migrations.Migration):

    dependencies = [
        ('test_success_reverse_halted', '0002_auto_20150109_1754'),
    ]

    operations = [
        migrations.RunPython(
            populate_data,
            populate_data_rev,
        ),
    ]
