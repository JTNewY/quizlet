# Generated by Django 5.1.2 on 2024-10-28 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0009_alter_englishword_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='unit',
            field=models.CharField(default='기타', max_length=20),
        ),
    ]
