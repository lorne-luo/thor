# Generated by Django 2.2.6 on 2020-01-28 22:59

from django.db import migrations, models
import django_countries.fields
import saleor.account.models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0034_service_account_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='user',
            name='openid',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=saleor.account.models.PossiblePhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone number'),
        ),
        migrations.AddField(
            model_name='user',
            name='province',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='sex'),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(blank=True, max_length=256, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='address',
            name='city_area',
            field=models.CharField(blank=True, max_length=128, verbose_name='District'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=django_countries.fields.CountryField(max_length=2, verbose_name='County'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country_area',
            field=models.CharField(blank=True, max_length=128, verbose_name='Province'),
        ),
        migrations.AlterField(
            model_name='address',
            name='first_name',
            field=models.CharField(blank=True, max_length=256, verbose_name='Given name'),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=saleor.account.models.PossiblePhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='address',
            name='street_address_1',
            field=models.CharField(blank=True, max_length=256, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=versatileimagefield.fields.VersatileImageField(blank=True, max_length=512, null=True, upload_to='user-avatars'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=256),
        ),
    ]
