# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_success', '0004_mymodel_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mymodel',
            name='title',
        ),
    ]
    
    def test_apply_success(self, apps, testcase):
        testcase.mymodel1.save()
