# Generated by Django 4.1.3 on 2023-09-16 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staticContentApp', '0002_alter_staticcontentmodel_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticcontentmodel',
            name='disableTitle',
            field=models.BooleanField(default=False),
        ),
    ]
