# Generated by Django 3.2.24 on 2024-02-29 13:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='dttotDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='DTTOT Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='DTTOT Updated at')),
                ('document_id', models.CharField(default=uuid.uuid4, editable=False, max_length=36)),
                ('dttot_id', models.CharField(default=uuid.uuid4, editable=False, max_length=20)),
                ('dttot_first_name', models.CharField(blank=True, max_length=50, verbose_name='DTTOT First Name')),
                ('dttot_last_name', models.CharField(blank=True, max_length=50, verbose_name='DTTOT Last Name')),
                ('dttot_type', models.CharField(max_length=50, verbose_name='DTTOT Type')),
                ('dttot_domicile_address1', models.TextField(blank=True, verbose_name='DTTOT Domicile Address')),
                ('dttot_domicile_rt', models.IntegerField(blank=True, verbose_name='DTTOT Domicile RT')),
                ('dttot_domicile_rw', models.IntegerField(blank=True, verbose_name='DTTOT Domicile RW')),
                ('dttot_domicile_kelurahan', models.CharField(blank=True, max_length=50, verbose_name='DTTOT Domicile Kelurahan')),
                ('dttot_domicile_kecamatan', models.CharField(blank=True, max_length=50, verbose_name='DTTOT Domicile Kecamatan')),
                ('dttot_domicile_kabupaten', models.CharField(blank=True, max_length=50, verbose_name='DTTOT Domicile Kabupaten')),
                ('dttot_domicile_kota', models.CharField(blank=True, max_length=50, verbose_name='DTTOT Domicile Kota')),
                ('dttot_domicile_provinsi', models.CharField(blank=True, max_length=50, verbose_name='DTTOT Domicile Provinsi')),
                ('dttot_domicile_postal_code', models.IntegerField(blank=True, verbose_name='DTTOT Domicile Postal code')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Created by User')),
            ],
        ),
    ]
