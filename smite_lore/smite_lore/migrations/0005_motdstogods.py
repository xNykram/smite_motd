# Generated by Django 3.2.5 on 2021-08-19 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smite_lore', '0004_auto_20210819_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotdsToGods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'MotdsToPrefGods',
                'managed': False,
            },
        ),
    ]