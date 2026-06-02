from django.db import migrations


def add_missing_donation_columns(apps, schema_editor):
    table_name = 'donations_donation'
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'PRAGMA table_info({table_name})')
        existing_columns = {row[1] for row in cursor.fetchall()}

    columns = {
        'title': "varchar(10) NOT NULL DEFAULT 'Mr'",
        'is_organization': 'bool NOT NULL DEFAULT 0',
        'country': "varchar(50) NOT NULL DEFAULT ''",
        'postcode': "varchar(20) NOT NULL DEFAULT ''",
        'in_country': "varchar(50) NOT NULL DEFAULT 'Tanzania'",
        'to_provide': "varchar(50) NOT NULL DEFAULT 'Nisomeshe'",
        'age_confirmation': 'bool NOT NULL DEFAULT 0',
        'contact_email': 'bool NOT NULL DEFAULT 0',
        'contact_sms': 'bool NOT NULL DEFAULT 0',
        'contact_whatsapp': 'bool NOT NULL DEFAULT 0',
        'contact_post': 'bool NOT NULL DEFAULT 0',
        'gift_aid': 'bool NOT NULL DEFAULT 0',
        'card_number': "varchar(16) NOT NULL DEFAULT ''",
        'expiry_date': "varchar(5) NOT NULL DEFAULT ''",
        'security_code': "varchar(4) NOT NULL DEFAULT ''",
        'agree_to_terms': 'bool NOT NULL DEFAULT 0',
    }

    for column_name, column_sql in columns.items():
        if column_name not in existing_columns:
            schema_editor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}')


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_repair_missing_payment_tables'),
    ]

    operations = [
        migrations.RunPython(add_missing_donation_columns, migrations.RunPython.noop),
    ]
