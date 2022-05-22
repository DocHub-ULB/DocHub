# Generated by Django 4.0.4 on 2022-05-22 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0010_category_course_trough"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursecategory",
            name="mandatory",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name="coursecategory",
            unique_together={("course", "category")},
        ),
    ]
