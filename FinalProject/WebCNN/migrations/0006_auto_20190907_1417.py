# Generated by Django 2.2.5 on 2019-09-07 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebCNN', '0005_auto_20190906_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='path',
            field=models.ImageField(blank=True, upload_to='origin/'),
        ),
    ]
