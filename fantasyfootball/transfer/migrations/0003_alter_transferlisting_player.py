import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transfer", "0002_initial"),
        ("player", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transferlisting",
            name="player",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transfer_listings",
                to="player.player",
            ),
        ),
    ]
