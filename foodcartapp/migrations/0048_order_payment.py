from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('C', 'Наличные'), ('N', 'Безналичные')], db_index=True, default='C', max_length=1, verbose_name='Способ оплаты'),
        ),
    ]
