# Generated by Django 5.1.3 on 2025-02-09 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("PassManagement", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="A",
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
                ("hash", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
