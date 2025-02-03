# Generated by Django 5.0 on 2025-02-03 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchaser_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('purchaser_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('purchaser_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('purchaser_phone_number', models.CharField(blank=True, max_length=25, null=True)),
            ],
            options={
                'db_table': 'session_attendee',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('capacity', models.IntegerField()),
            ],
            options={
                'db_table': 'event',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
            ],
            options={
                'db_table': 'event_session',
            },
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, choices=[('host', 'Host'), ('participant', 'Prefer Not to Say')], default='host', max_length=50)),
            ],
            options={
                'db_table': 'speaker',
            },
        ),
    ]
