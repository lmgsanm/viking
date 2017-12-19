# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-13 08:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0004_remove_server_iaas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='cpu_core',
            field=models.IntegerField(choices=[(1, '1 Core'), (2, '2 Core'), (4, '4 Core'), (8, '8 Core')], default=1, verbose_name='cpu core number'),
        ),
        migrations.AlterField(
            model_name='server',
            name='cpu_type',
            field=models.CharField(choices=[('Intel Xeon CPU', 'Entry Level'), ('Intel Xeon Platinum 8163', 'General Level'), ('Intel Xeon E5-2682v4', 'Enhance Level'), ('Intel Xeon Gold 6149', 'Supreme Level')], default='Intel Xeon CPU', max_length=50, verbose_name='cpu type'),
        ),
    ]
