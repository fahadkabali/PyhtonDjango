# Generated by Django 4.1.2 on 2024-07-15 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0006_alter_customuser_profile_pic"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="profile_pic",
        ),
        migrations.AddField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="default.jpg",
                null=True,
                upload_to="profile_images/",
            ),
        ),
        migrations.AddField(
            model_name="customuser",
            name="bio",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="fullname",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="organisation_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
