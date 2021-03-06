# Generated by Django 2.2.6 on 2020-01-29 03:45

import django.core.validators
from django.db import migrations, models
import saleor.account.models
import saleor.core.django.storage
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0035_auto_20200129_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='id_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='ID number'),
        ),
        migrations.AddField(
            model_name='address',
            name='id_photo_back',
            field=stdimage.models.StdImageField(blank=True, null=True, storage=saleor.core.django.storage.OverwriteStorage(), upload_to=saleor.account.models.get_id_photo_back_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'gif', 'png'])], verbose_name='ID Back'),
        ),
        migrations.AddField(
            model_name='address',
            name='id_photo_front',
            field=stdimage.models.StdImageField(blank=True, null=True, storage=saleor.core.django.storage.OverwriteStorage(), upload_to=saleor.account.models.get_id_photo_front_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'gif', 'png'])], verbose_name='ID Front'),
        ),
    ]
