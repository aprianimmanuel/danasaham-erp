# Generated by Django 3.2.24 on 2024-03-05 06:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20240305_0432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dttotdoc',
            name='input_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by User'),
        ),
    ]
