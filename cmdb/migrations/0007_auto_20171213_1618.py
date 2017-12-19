# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-13 08:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0006_auto_20171213_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date server created'),
        ),
        migrations.AlterField(
            model_name='server',
            name='outer_ip',
            field=models.CharField(max_length=20, null=True, verbose_name='outer ip'),
        ),
    ]
