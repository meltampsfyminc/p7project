# Migration to remove price field from Property

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0010_property_building_integration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='price',
        ),
    ]
