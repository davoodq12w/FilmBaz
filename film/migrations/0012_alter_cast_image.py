# Generated by Django 5.1 on 2024-08-18 08:37

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('film', '0011_file_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cast',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format=None, keep_meta=True, quality=50, scale=None, size=[200, 200], upload_to='casts/'),
        ),
    ]
