from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0003_repair_donation_columns'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='donation',
                    name='giving_frequency',
                    field=models.CharField(default='one-off', max_length=20),
                ),
                migrations.AddField(
                    model_name='donation',
                    name='payment_method',
                    field=models.CharField(default='mobile', max_length=20),
                ),
                migrations.AddField(
                    model_name='donation',
                    name='status',
                    field=models.CharField(default='pending', max_length=10),
                ),
                migrations.AddField(
                    model_name='donation',
                    name='updated_at',
                    field=models.DateTimeField(auto_now=True),
                ),
            ],
        ),
    ]
