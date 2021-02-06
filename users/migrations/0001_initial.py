import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('netid', models.CharField(unique=True, max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=127)),
                ('last_name', models.CharField(max_length=127)),
                ('email', models.CharField(unique=True, max_length=255)),
                ('registration', models.CharField(max_length=80, blank=True)),
                ('photo', models.CharField(default='', max_length=10)),
                ('welcome', models.BooleanField(default=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_academic', models.BooleanField(default=False)),
                ('is_representative', models.BooleanField(default=False)),
                ('followed_courses', models.ManyToManyField(to='catalog.Course')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('faculty', models.CharField(max_length=80, null=True)),
                ('section', models.CharField(max_length=80, null=True)),
                ('year', models.PositiveIntegerField(null=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='inscription',
            unique_together={('user', 'section', 'faculty', 'year')},
        ),
    ]
