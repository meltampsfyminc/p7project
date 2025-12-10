# Generated migration for timezone and currency fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0008_itemtransfer_is_scrapped_itemtransfer_scrap_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='timezone',
            field=models.CharField(
                choices=[
                    ('PHT', 'Philippine Time (UTC+08:00)'),
                    ('EST', 'Eastern Standard Time (UTC-05:00)'),
                    ('UTC', 'Coordinated Universal Time (UTC±00:00)'),
                    ('CET', 'Central European Time (UTC+01:00)'),
                ],
                default='PHT',
                help_text="User's preferred timezone for datetime display",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='currency',
            field=models.CharField(
                choices=[
                    ('PHP', 'Philippine Peso (₱)'),
                    ('USD', 'US Dollar ($)'),
                    ('EUR', 'Euro (€)'),
                ],
                default='PHP',
                help_text="User's preferred currency for financial displays",
                max_length=3,
            ),
        ),
    ]
