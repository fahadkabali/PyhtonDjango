# Generated by Django 5.0.6 on 2024-07-11 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_userresponse_total_score"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userresponse",
            name="total_score",
        ),
    ]
