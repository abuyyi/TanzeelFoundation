import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Validate that a fixture file is valid UTF-8 JSON before loading it.'

    def add_arguments(self, parser):
        parser.add_argument('fixture', nargs='?', default='data.json', help='Path to the fixture file to validate.')

    def handle(self, *args, **options):
        fixture_path = Path(options['fixture'])
        if not fixture_path.exists():
            raise CommandError(f'Fixture file not found: {fixture_path}')

        try:
            raw_bytes = fixture_path.read_bytes()
            text = raw_bytes.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise CommandError(f'{fixture_path} is not valid UTF-8: {exc}') from exc

        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            raise CommandError(f'{fixture_path} is not valid JSON: {exc}') from exc

        self.stdout.write(
            self.style.SUCCESS(f'{fixture_path} is valid UTF-8 JSON ({fixture_path.stat().st_size} bytes).')
        )
