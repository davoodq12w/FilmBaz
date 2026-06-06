import json
from django.core.management.base import BaseCommand
from django.db import transaction
from film.models import Movie
from people.models import Cast, CrewMember, MovieCrew


class Command(BaseCommand):
    help = 'ایجاد روابط بین فیلم‌ها، بازیگران و عوامل تولید از فایل movie_relations.json'

    @transaction.atomic
    def handle(self, *args, **options):
        # مسیر فایل را بر اساس ساختار پروژه خود تنظیم کنید
        file_path = "film/management/fixtures/movie_relations.json"

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                relations_data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ فایل یافت نشد: {file_path}'))
            return

        success_count = 0

        for item in relations_data:
            movie_slug = item.get("movie_slug")

            # پیدا کردن فیلم مربوطه
            try:
                movie = Movie.objects.get(slug=movie_slug)
            except Movie.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠️ فیلم با شناسه {movie_slug} یافت نشد.'))
                continue

            # ۱. برقراری ارتباط بازیگران
            # مثال: پیدا کردن تمام رکوردهای بازیگران که شناسه آنها در لیست casts است و اتصال آنها به فیلم
            cast_slugs = item.get("casts", [])
            if cast_slugs:
                casts_queryset = Cast.objects.filter(slug__in=cast_slugs)
                movie.casts.set(casts_queryset)

            # ۲. برقراری ارتباط عوامل تولید از طریق مدل واسط (MovieCrew)
            # مثال: ثبت کریستوفر نولان به عنوان کارگردان برای فیلم اینتراستلار
            crew_list = item.get("crew", [])
            for crew_data in crew_list:
                crew_slug = crew_data.get("slug")
                role = crew_data.get("role")

                try:
                    crew_member = CrewMember.objects.get(slug=crew_slug)
                    MovieCrew.objects.update_or_create(
                        movie=movie,
                        crew=crew_member,
                        role=role
                    )
                except CrewMember.DoesNotExist:
                    continue

            success_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ روابط {success_count} فیلم با موفقیت برقرار شد!'))
