# Generated by Django 4.1.2 on 2024-07-31 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0005_assessmenthistory_certificate"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessmenthistory",
            name="score_color",
            field=models.CharField(default="red", max_length=20),
        ),
    ]
