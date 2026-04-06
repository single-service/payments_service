from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refunds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='additional_data',
            field=models.JSONField(blank=True, default=None, null=True, verbose_name='Additional data'),
        ),
    ]
