# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-04-16 21:31
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0035_auto_20200408_2126'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resource',
            old_name='additional_details',
            new_name='extra_data',
        ),
        migrations.AddField(
            model_name='package',
            name='last_modified_date',
            field=models.DateTimeField(blank=True, db_index=True, help_text='Timestamp set when a Package is created or modified', null=True),
        ),
    ]