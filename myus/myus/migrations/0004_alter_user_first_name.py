# Generated by Django 4.2.4 on 2023-08-30 09:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myus", "0003_auto_20200630_0247"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
    ]
