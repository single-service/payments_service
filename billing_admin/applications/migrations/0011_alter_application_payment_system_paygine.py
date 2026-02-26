from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0010_application_sno_application_tax'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='payment_system',
            field=models.IntegerField(
                choices=[(1, 'Dummy'), (2, 'ROBOKASSA'), (3, 'YKASSA'), (4, 'PAYGINE')],
                verbose_name='Payment System',
            ),
        ),
        migrations.AlterField(
            model_name='paymentsystemparamter',
            name='payment_system',
            field=models.IntegerField(
                choices=[(1, 'Dummy'), (2, 'ROBOKASSA'), (3, 'YKASSA'), (4, 'PAYGINE')],
                verbose_name='Payment System',
            ),
        ),
    ]
