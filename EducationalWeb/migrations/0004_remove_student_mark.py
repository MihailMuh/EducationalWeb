# Generated by Django 4.0 on 2022-06-09 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EducationalWeb', '0003_alter_mark_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='mark',
        ),
    ]