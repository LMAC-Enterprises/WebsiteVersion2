# Generated by Django 4.1.3 on 2022-12-27 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LMACPollPostTemplateModel',
            fields=[
                ('name', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('tags', models.CharField(max_length=256)),
                ('body', models.TextField()),
                ('beneficiaries', models.TextField()),
            ],
            options={
                'verbose_name': 'Poll Post Template',
                'db_table': 'poll_post_template',
                'permissions': [('manage poll post templates', 'Allows to manage poll post templates.')],
            },
        ),
    ]