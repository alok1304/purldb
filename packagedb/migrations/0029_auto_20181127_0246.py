# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-27 02:46
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0028_auto_20181127_0224'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='normalized_license',
            new_name='license_expression',
        ),
    ]