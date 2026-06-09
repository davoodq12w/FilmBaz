import json
from django.core.management.base import BaseCommand
from people.models import Cast


class Command(BaseCommand):
    help = 'وارد کردن لیست بازیگران از فایل casts.json'

    def handle(self, *args, **kwargs):
        file_path = "people/management/fixtures/casts.json"

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                casts_data = json.load(file)

            created_count = 0
            updated_count = 0

            for item in casts_data:
                cast, created = Cast.objects.update_or_create(
                    slug=item['slug'],
                    defaults={
                        'fa_name': item['fa_name'],
                        'en_name': item['en_name']
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1


            self.stdout.write(
                self.style.SUCCESS(
                    f"بازیگران || ساخته شده ها: {created_count} | آپدیت شده ها: {updated_count}"
                )
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {file_path}")
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(str(e))
            )