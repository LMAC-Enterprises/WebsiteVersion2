# Generated by Django 4.1.3 on 2022-12-19 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lilGallery', '0002_alter_lilratingsmodel_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='LILTagsModel',
            fields=[
                ('tagText', models.CharField(max_length=512, primary_key=True, serialize=False)),
                ('hits', models.IntegerField()),
            ],
            options={
                'db_table': 'LMACGalleryTags',
                'managed': False,
            },
        ),
    ]