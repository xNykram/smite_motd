# Generated by Django 3.2.5 on 2021-09-30 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smite_lore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tierlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('godName', models.CharField(max_length=128)),
                ('mode', models.CharField(max_length=64)),
                ('rank', models.CharField(max_length=12)),
                ('winrate', models.FloatField(null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]