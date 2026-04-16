from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_ingrediente_stock_productoingrediente_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='disponible',
            field=models.BooleanField(
                default=True,
                help_text='Visible en el menú POS',
            ),
        ),
    ]
