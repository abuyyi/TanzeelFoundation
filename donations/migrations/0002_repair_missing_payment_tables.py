from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                CREATE TABLE IF NOT EXISTS donations_paymenttransaction (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    external_id varchar(64) NOT NULL UNIQUE,
                    idempotency_key varchar(64) NOT NULL UNIQUE,
                    provider varchar(32) NOT NULL,
                    phone_number varchar(20) NOT NULL,
                    amount decimal NOT NULL,
                    currency varchar(8) NOT NULL,
                    status varchar(16) NOT NULL,
                    gateway_reference varchar(128) NOT NULL,
                    gateway_status varchar(64) NOT NULL,
                    gateway_message text NOT NULL,
                    callback_hash varchar(64) NOT NULL,
                    callback_verified_at datetime NULL,
                    completed_at datetime NULL,
                    initiation_attempts integer unsigned NOT NULL CHECK (initiation_attempts >= 0),
                    last_initiation_at datetime NULL,
                    next_retry_at datetime NULL,
                    last_error_at datetime NULL,
                    request_payload text NOT NULL,
                    response_payload text NOT NULL,
                    callback_payload text NOT NULL,
                    created_at datetime NOT NULL,
                    updated_at datetime NOT NULL,
                    donation_id bigint NOT NULL REFERENCES donations_donation (id) DEFERRABLE INITIALLY DEFERRED
                )
                """,
                "CREATE INDEX IF NOT EXISTS donations_paymenttransaction_status_idx ON donations_paymenttransaction (status)",
                "CREATE INDEX IF NOT EXISTS donations_paymenttransaction_gateway_reference_idx ON donations_paymenttransaction (gateway_reference)",
                "CREATE INDEX IF NOT EXISTS donations_paymenttransaction_donation_id_idx ON donations_paymenttransaction (donation_id)",
                """
                CREATE TABLE IF NOT EXISTS donations_azampaywebhookevent (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    event_hash varchar(64) NOT NULL,
                    external_id varchar(64) NOT NULL,
                    gateway_reference varchar(128) NOT NULL,
                    headers text NOT NULL,
                    payload text NOT NULL,
                    verification_passed bool NOT NULL,
                    duplicate bool NOT NULL,
                    processed bool NOT NULL,
                    processing_note varchar(255) NOT NULL,
                    received_at datetime NOT NULL,
                    transaction_id bigint NULL REFERENCES donations_paymenttransaction (id) DEFERRABLE INITIALLY DEFERRED
                )
                """,
                "CREATE INDEX IF NOT EXISTS donations_azampaywebhookevent_event_hash_idx ON donations_azampaywebhookevent (event_hash)",
                "CREATE INDEX IF NOT EXISTS donations_azampaywebhookevent_external_id_idx ON donations_azampaywebhookevent (external_id)",
                "CREATE INDEX IF NOT EXISTS donations_azampaywebhookevent_gateway_reference_idx ON donations_azampaywebhookevent (gateway_reference)",
                "CREATE INDEX IF NOT EXISTS donations_azampaywebhookevent_transaction_id_idx ON donations_azampaywebhookevent (transaction_id)",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
