# Generated migration to add validation_data to CartItem

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0015_merge_20250714_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='validation_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]