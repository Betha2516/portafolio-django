# Generated by Django 5.1.7 on 2025-05-20 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portafolio', '0004_comment_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
