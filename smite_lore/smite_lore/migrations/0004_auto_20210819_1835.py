# Generated by Django 3.2.5 on 2021-08-19 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smite_lore', '0003_auto_20210819_1833'),
    ]

    operations = [
        migrations.RenameField(
            model_name='motd',
            old_name='mod_id',
            new_name='modID',
        ),
        migrations.RenameField(
            model_name='prefgodsformotd',
            old_name='god_id',
            new_name='godID',
        ),
        migrations.RenameField(
            model_name='prefgodsformotd',
            old_name='god_image_url',
            new_name='godImageUrl',
        ),
        migrations.RenameField(
            model_name='prefgodsformotd',
            old_name='god_name',
            new_name='godName',
        ),
        migrations.RenameField(
            model_name='prefgodsformotd',
            old_name='motd_id',
            new_name='motdID',
        ),
    ]
