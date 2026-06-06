import json
from django.core.management.base import BaseCommand
from people.models import CrewMember  # نام your_app را با نام اپلیکیشن خود جایگزین کنید


class Command(BaseCommand):
    help = 'وارد کردن لیست عوامل تولید از فایل crew_members.json'

    def handle(self, *args, **kwargs):
        file_path = "people/management/fixtures/crew_members.json"

        with open(file_path, 'r', encoding='utf-8') as file:
            crew_data = json.load(file)

        for item in crew_data:
            CrewMember.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'fa_name': item['fa_name'],
                    'en_name': item['en_name']
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ عوامل تولید با موفقیت وارد دیتابیس شدند!'))
