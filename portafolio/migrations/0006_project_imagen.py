# Generated by Django 5.1.7 on 2025-05-20 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portafolio', '0005_alter_comment_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='proyectos/'),
        ),
    ]
