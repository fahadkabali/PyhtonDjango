# Generated by Django 5.0.6 on 2024-07-11 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userresponse",
            name="total_score",
            field=models.IntegerField(default=0),
        ),
    ]
