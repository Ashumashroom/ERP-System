# Generated by Django 4.2.5 on 2024-12-07 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_todoitem_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='todoitem',
            name='is_important',
            field=models.BooleanField(default=False),
        ),
    ]
