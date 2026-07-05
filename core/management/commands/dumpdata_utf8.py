import io
import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Export Django fixture data as UTF-8 JSON instead of relying on shell redirection.'

    def add_arguments(self, parser):
        parser.add_argument('output', nargs='?', default='data.json', help='Path to the JSON fixture file to write.')
        parser.add_argument('--indent', type=int, default=2, help='JSON indentation level.')
        parser.add_argument('--natural-foreign', action='store_true', default=True, help='Use natural foreign keys in the export.')
        parser.add_argument('--natural-primary', action='store_true', default=True, help='Use natural primary keys in the export.')
        parser.add_argument('--exclude', action='append', default=[], help='App label or model to exclude from the export.')
        parser.add_argument('--database', default='default', help='Database alias to dump from.')
        parser.add_argument('--format', default='json', help='Fixture format.')

    def handle(self, *args, **options):
        output_path = Path(options['output'])
        buffer = io.StringIO()

        try:
            call_command(
                'dumpdata',
                stdout=buffer,
                format=options['format'],
                indent=options['indent'],
                natural_foreign=options['natural_foreign'],
                natural_primary=options['natural_primary'],
                database=options['database'],
                exclude=options['exclude'],
            )
        except Exception as exc:
            raise CommandError(f'Failed to export fixture data: {exc}') from exc

        content = buffer.getvalue()
        if not content.endswith('\n'):
            content += '\n'

        try:
            json.loads(content)
        except json.JSONDecodeError as exc:
            raise CommandError(f'Generated fixture is not valid JSON: {exc}') from exc

        output_path.write_text(content, encoding='utf-8')
        self.stdout.write(
            self.style.SUCCESS(f'Wrote UTF-8 fixture to {output_path} ({output_path.stat().st_size} bytes).')
        )
