# Generated by Django 4.0 on 2022-06-09 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EducationalWeb', '0002_alter_mark_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mark',
            name='weight',
            field=models.PositiveSmallIntegerField(),
        ),
    ]