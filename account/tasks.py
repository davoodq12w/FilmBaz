import requests
from celery import shared_task
from django.core.mail import send_mail
from film.models import Movie
from django.db.models import Count
from account.models import UserRecommendation, FilmBazUser


@shared_task(queue="default")
def send_confirm_email(username, email):
    message = f" عزیز از بازخورد شما ممنونیم{username} \n\n \n با تشکر , فیمباز "
    send_mail(
        subject="ارسال تیکت موفقیت آمیز بود",
        message=message,
        from_email="davodrashiworking@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task()
def get_recommendation_movies():
    popular_movies = Movie.objects.annotate(popularity=Count("interactions")).order_by("-popularity")[:100]
    movie_ids = [m.id for m in popular_movies]

    url = f"http://ml_service:8002/recomendation/get_movies/"
    for user in FilmBazUser.objects.all():
        if user.interactions.count() > 1:
            continue

        data = {
            "user_id": user.id,
            "movie_ids": movie_ids,
        }
        response = requests.post(url, json=data)
        response.raise_for_status()

        recommendations = [
            {
                "movie_id": movie_id,
                "score": score,
            }
            for movie_id, score in response.json()
        ]
        UserRecommendation.objects.update_or_create(
            user_id=user.id,
            defaults={
                "recommendations": recommendations,
            },
        )
