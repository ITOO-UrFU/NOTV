# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-16 04:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='title',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Название страницы'),
        ),
    ]
