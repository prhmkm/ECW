# Generated by Django 4.2.5 on 2023-10-21 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OCT', '0016_alter_dailytasks_goal_related_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlytasks',
            name='checked_by_admin',
            field=models.BooleanField(default=False),
        ),
    ]