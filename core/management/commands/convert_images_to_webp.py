from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ImageField

from core.utils.image_optimizer import optimize_model_image_field


class Command(BaseCommand):
    help = 'Convert existing image file fields in the database to optimized WebP images.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            dest='app_label',
            help='Optional app label to process only one app',
        )
        parser.add_argument(
            '--model',
            dest='model_name',
            help='Optional model name to process only one model',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report the number of images that would be converted without saving changes',
        )

    def handle(self, *args, **options):
        app_label = options.get('app_label')
        model_name = options.get('model_name')
        dry_run = options.get('dry_run', False)

        models = []
        if app_label:
            try:
                app_config = apps.get_app_config(app_label)
                models = list(app_config.get_models())
            except LookupError:
                self.stderr.write(self.style.ERROR(f"App '{app_label}' not found."))
                return
        else:
            models = apps.get_models()

        total_converted = 0
        total_skipped = 0
        total_models = 0
        total_images = 0

        for model in models:
            if model_name and model.__name__.lower() != model_name.lower():
                continue

            image_fields = [f.name for f in model._meta.fields if isinstance(f, ImageField)]
            if not image_fields:
                continue

            total_models += 1
            self.stdout.write(self.style.NOTICE(f"Processing model: {model.__name__}"))
            queryset = model.objects.all()
            model_processed = 0
            model_converted = 0
            model_skipped = 0

            for instance in queryset:
                for field_name in image_fields:
                    field_file = getattr(instance, field_name, None)
                    if not field_file or not getattr(field_file, 'name', None):
                        model_skipped += 1
                        continue

                    if field_file.name.lower().endswith('.webp'):
                        model_skipped += 1
                        continue

                    total_images += 1
                    if dry_run:
                        self.stdout.write(
                            f"Would convert: {model.__name__}.{field_name} -> {field_file.name}"
                        )
                        continue

                    converted = optimize_model_image_field(instance, field_name)
                    if converted:
                        model_converted += 1
                        total_converted += 1
                    else:
                        model_skipped += 1

                model_processed += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{model.__name__}: scanned {model_processed} row(s), "
                    f"converted {model_converted}, skipped {model_skipped}"
                )
            )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"Dry run complete. {total_images} image(s) would be processed."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Conversion complete across {total_models} model(s): "
                f"{total_converted} image(s) converted."))
