import json
from django.core.management.base import BaseCommand
from people.models import Cast

class Command(BaseCommand):
    help = 'وارد کردن لیست بازیگران از فایل casts.json'

    def handle(self, *args, **kwargs):
        file_path = "people/management/fixtures/casts.json"

        # مسیر فایل را بر اساس محل قرارگیری فایل در پروژه تنظیم کنید
        with open(file_path, 'r', encoding='utf-8') as file:
            casts_data = json.load(file)

        for item in casts_data:
            # استفاده از update_or_create برای جلوگیری از خطای تکرار (Duplicate)
            Cast.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'fa_name': item['fa_name'],
                    'en_name': item['en_name']
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ بازیگران با موفقیت وارد دیتابیس شدند!'))
