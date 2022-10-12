# Generated by Django 4.1.1 on 2022-10-12 08:54

from django.db import migrations, models

import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("netid", models.CharField(max_length=20, unique=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("edited", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=127)),
                ("last_name", models.CharField(max_length=127)),
                ("email", models.CharField(max_length=255, unique=True)),
                ("welcome", models.BooleanField(default=True)),
                ("comment", models.TextField(blank=True, default="")),
                ("register_method", models.CharField(max_length=32)),
                ("last_login_method", models.CharField(max_length=32)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_academic", models.BooleanField(default=False)),
                ("is_representative", models.BooleanField(default=False)),
                ("notify_on_response", models.BooleanField(default=True)),
                ("notify_on_new_doc", models.BooleanField(default=True)),
                ("notify_on_new_thread", models.BooleanField(default=True)),
                (
                    "moderated_courses",
                    models.ManyToManyField(blank=True, to="catalog.course"),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", users.models.CustomUserManager()),
            ],
        ),
    ]
