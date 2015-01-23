# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_success', '0003_auto_20150109_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymodel',
            name='title',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
    ]
    
    def test_apply_success(self, apps, testcase):
        testcase.mymodel1.save()
