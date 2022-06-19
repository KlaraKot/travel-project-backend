# Generated by Django 4.0.4 on 2022-06-11 14:32

import django.contrib.auth.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cityName', models.CharField(max_length=200)),
                ('country', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=700)),
                ('monuments', models.CharField(max_length=400)),
                ('averageRate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='cityRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cityName', models.CharField(max_length=200)),
                ('rate', models.IntegerField()),
                ('userId', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='HistoryRecord',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('actionType', models.IntegerField()),
                ('actionContent', models.IntegerField()),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='HistoryService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('HistoryRecordCount', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='lastId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lastId', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('country', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('visitedPlaces', models.CharField(max_length=200)),
                ('preferencePlaces', models.CharField(max_length=200)),
                ('language', models.CharField(max_length=200)),
                ('seaOrMountains', models.CharField(max_length=200)),
                ('companion', models.CharField(max_length=200)),
                ('wheelchair', models.BooleanField(default=False)),
                ('animals', models.BooleanField(default=False)),
                ('listOfPreferences', models.CharField(max_length=200)),
                ('weather', models.CharField(max_length=200)),
                ('typeOfCity', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=200)),
                ('surname', models.CharField(max_length=200)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=200)),
                ('age', models.IntegerField()),
                ('email', models.CharField(max_length=200, unique=True)),
                ('password', models.CharField(max_length=200)),
                ('languageNative', models.CharField(max_length=200)),
                ('languageForeign', models.CharField(max_length=200)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
