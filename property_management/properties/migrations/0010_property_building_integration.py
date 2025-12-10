# Migration to integrate Property model with HousingUnit

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0009_userprofile_timezone_and_currency'),
    ]

    operations = [
        # Enhance Property model
        migrations.RemoveField(
            model_name='property',
            name='bedrooms',
        ),
        migrations.RemoveField(
            model_name='property',
            name='bathrooms',
        ),
        migrations.RemoveField(
            model_name='property',
            name='square_feet',
        ),
        migrations.AlterField(
            model_name='property',
            name='name',
            field=models.CharField(help_text="Building name (e.g., 'Abra Building')", max_length=255),
        ),
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.CharField(help_text='Street address', max_length=500),
        ),
        migrations.AlterField(
            model_name='property',
            name='city',
            field=models.CharField(help_text='City/Municipality', max_length=100),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(help_text="Type of property (e.g., 'Building', 'Residential', 'Commercial')", max_length=100),
        ),
        migrations.RenameField(
            model_name='property',
            old_name='state',
            new_name='province',
        ),
        migrations.AddField(
            model_name='property',
            name='owner',
            field=models.CharField(default='Unknown', help_text="Property owner (e.g., 'The Church')", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='total_units',
            field=models.IntegerField(default=0, help_text='Total number of housing units in this property'),
        ),
        migrations.AddField(
            model_name='property',
            name='acquisition_cost',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Property acquisition cost (PHP)', max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='current_value',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Current estimated property value (PHP)', max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('inactive', 'Inactive'),
                    ('maintenance', 'Under Maintenance'),
                    ('sold', 'Sold'),
                ],
                default='active',
                max_length=20,
            ),
        ),
        # Update HousingUnit model
        migrations.RemoveField(
            model_name='housingunit',
            name='building',
        ),
        migrations.AddField(
            model_name='housingunit',
            name='property',
            field=models.ForeignKey(
                blank=True,
                help_text='The building/property this unit belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='housing_units',
                to='properties.property',
            ),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='occupant_name',
            field=models.CharField(help_text='Name of occupant/unit head', max_length=255),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='department',
            field=models.CharField(blank=True, help_text='Department of occupant', max_length=255),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='section',
            field=models.CharField(blank=True, help_text='Section/Team of occupant', max_length=255),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='job_title',
            field=models.CharField(blank=True, help_text='Job title of occupant', max_length=255),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='housing_unit_name',
            field=models.CharField(blank=True, help_text="Display name (e.g., 'Room 101')", max_length=100),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='floor',
            field=models.CharField(blank=True, help_text='Floor number/level', max_length=50),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='unit_number',
            field=models.CharField(help_text="Unit number/identifier (e.g., '101', '102', 'Unit A')", max_length=100),
        ),
        migrations.AlterField(
            model_name='housingunit',
            name='address',
            field=models.CharField(blank=True, help_text='Full address of the unit', max_length=500),
        ),
    ]
