# Generated by Django 5.1.3 on 2024-11-14 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='member_id',
        ),
        migrations.AlterField(
            model_name='member',
            name='contact_number',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
