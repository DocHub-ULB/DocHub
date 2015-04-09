# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('polydag', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read', models.BooleanField(default=False, db_index=True)),
                ('node', models.ForeignKey(to='polydag.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PreNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('text', models.CharField(max_length=160)),
                ('sender_type', models.CharField(max_length=160)),
                ('sender_info', models.CharField(default='', max_length=160)),
                ('delivered', models.BooleanField(default=False, db_index=True)),
                ('url', models.URLField()),
                ('personal', models.BooleanField(default=False, db_index=True)),
                ('icon', models.CharField(default='megaphone', max_length=50)),
                ('node', models.ForeignKey(to='polydag.Node')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='notification',
            name='prenotif',
            field=models.ForeignKey(to='notify.PreNotification'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
