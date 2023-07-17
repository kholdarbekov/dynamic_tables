# Generated by Django 4.2.3 on 2023-07-16 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DynamicModelField",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("type", models.CharField(max_length=128)),
                ("options", models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="DynamicModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256, unique=True)),
                ("options", models.JSONField(blank=True, null=True)),
                ("admin_opts", models.JSONField(blank=True, null=True)),
                ("fields", models.ManyToManyField(to="tables.dynamicmodelfield")),
            ],
        ),
    ]
