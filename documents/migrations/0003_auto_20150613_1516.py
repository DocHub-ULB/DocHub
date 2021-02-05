from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20150612_1735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='words',
        ),
        migrations.AlterField(
            model_name='document',
            name='downloads',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='pages',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='size',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='views',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='height_120',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='height_600',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='height_900',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
