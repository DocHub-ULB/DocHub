from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documents', '0001_initial'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('edited', models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('edited', models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)),
                ('placement', models.TextField(default=None, null=True)),
                ('course', models.ForeignKey(on_delete=models.deletion.CASCADE, to='catalog.Course')),
                ('document', models.ForeignKey(on_delete=models.deletion.CASCADE, to='documents.Document', null=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='telepathy.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
