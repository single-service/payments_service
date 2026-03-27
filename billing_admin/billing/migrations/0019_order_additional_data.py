from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0018_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='additional_data',
            field=models.JSONField(blank=True, default=None, null=True, verbose_name='Additional Data'),
        ),
    ]
