import requests
from celery import shared_task
from django.core.mail import send_mail
from film.models import Movie
from django.db.models import Count


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

@shared_task(queue="recommendation")
def get_recommendation_movie(user_id):
    popular_movies = Movie.objects.annotate(popularity=Count("interactions")).order_by("-popularity")[:100]
    movie_ids = [m.id for m in popular_movies]

    url = f"http://ml_service:8002/recomendation/get_movies/"
    data = {
        "user_id": user_id,
        "movie_ids": movie_ids,
    }
    response = requests.post(url, json=data)

    print(response.json())


