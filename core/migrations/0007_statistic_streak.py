# Generated by Django 2.1.7 on 2019-05-09 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20190501_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='streak',
            field=models.IntegerField(default=0),
        ),
    ]