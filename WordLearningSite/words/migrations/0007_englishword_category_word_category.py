# Generated by Django 5.1.2 on 2024-10-28 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0006_visitorcount'),
    ]

    operations = [
        migrations.AddField(
            model_name='englishword',
            name='category',
            field=models.CharField(choices=[('Other', 'Other'), ('Unit 1', 'Unit 1'), ('Unit 2', 'Unit 2'), ('Unit 3', 'Unit 3')], default='Other', max_length=10),
        ),
        migrations.AddField(
            model_name='word',
            name='category',
            field=models.CharField(choices=[('Other', 'Other'), ('Unit 1', 'Unit 1'), ('Unit 2', 'Unit 2'), ('Unit 3', 'Unit 3')], default='Other', max_length=10),
        ),
    ]
