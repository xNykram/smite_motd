# Generated by Django 3.2.5 on 2021-08-19 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smite_lore', '0005_motdstogods'),
    ]

    operations = [
        migrations.RenameField(
            model_name='motd',
            old_name='modID',
            new_name='motdID',
        ),
    ]