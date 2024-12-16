# Generated by Django 5.1.2 on 2024-11-27 23:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matchcode", "0003_snippetindex"),
        ("packagedb", "0086_alter_party_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="snippetindex",
            name="position",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="approximatedirectorycontentindex",
            name="package",
            field=models.ForeignKey(
                help_text="The Package that this file is from",
                on_delete=django.db.models.deletion.CASCADE,
                to="packagedb.package",
            ),
        ),
        migrations.AlterField(
            model_name="approximatedirectorystructureindex",
            name="package",
            field=models.ForeignKey(
                help_text="The Package that this file is from",
                on_delete=django.db.models.deletion.CASCADE,
                to="packagedb.package",
            ),
        ),
        migrations.AlterField(
            model_name="approximateresourcecontentindex",
            name="package",
            field=models.ForeignKey(
                help_text="The Package that this file is from",
                on_delete=django.db.models.deletion.CASCADE,
                to="packagedb.package",
            ),
        ),
        migrations.AlterField(
            model_name="snippetindex",
            name="package",
            field=models.ForeignKey(
                help_text="The Package that this file is from",
                on_delete=django.db.models.deletion.CASCADE,
                to="packagedb.package",
            ),
        ),
        migrations.CreateModel(
            name="ApproximateFileIndex",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "indexed_elements_count",
                    models.IntegerField(
                        help_text="Number of elements that went into the fingerprint"
                    ),
                ),
                (
                    "chunk1",
                    models.BinaryField(
                        db_index=True,
                        help_text="Binary form of the first 8 (0-7) hex digits of the fingerprint",
                        max_length=4,
                    ),
                ),
                (
                    "chunk2",
                    models.BinaryField(
                        db_index=True,
                        help_text="Binary form of the second 8 (8-15) hex digits of the fingerprint",
                        max_length=4,
                    ),
                ),
                (
                    "chunk3",
                    models.BinaryField(
                        db_index=True,
                        help_text="Binary form of the third 8 (16-23) hex digits of the fingerprint",
                        max_length=4,
                    ),
                ),
                (
                    "chunk4",
                    models.BinaryField(
                        db_index=True,
                        help_text="Binary form of the fourth 8 (24-32) hex digits of the fingerprint",
                        max_length=4,
                    ),
                ),
                (
                    "path",
                    models.CharField(
                        help_text="The full path value of this resource",
                        max_length=2000,
                    ),
                ),
                (
                    "package",
                    models.ForeignKey(
                        help_text="The Package that this file is from",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="packagedb.package",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {
                    ("chunk1", "chunk2", "chunk3", "chunk4", "package", "path")
                },
            },
        ),
    ]
