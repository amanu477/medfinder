# Generated migration for scheduled order fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_scheduled',
            field=models.BooleanField(default=False, help_text='Whether this order was scheduled for when pharmacy opens'),
        ),
        migrations.AddField(
            model_name='order',
            name='scheduled_for',
            field=models.DateTimeField(blank=True, null=True, help_text='When this order is scheduled to be processed'),
        ),
        migrations.AddField(
            model_name='order',
            name='scheduled_message',
            field=models.TextField(blank=True, null=True, help_text='Message explaining when order is scheduled'),
        ),
        migrations.AddField(
            model_name='order',
            name='pharmacy_response',
            field=models.TextField(blank=True, null=True, help_text='Pharmacy response to scheduled order'),
        ),
    ]