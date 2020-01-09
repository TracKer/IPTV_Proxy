# Generated by Django 3.0.2 on 2020-01-09 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.FloatField()),
                ('name', models.CharField(max_length=255)),
                ('name_original', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'New'), (1, 'Available'), (2, 'Watched')], default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='main.Source')),
            ],
            options={
                'db_table': 'segment',
            },
        ),
    ]
