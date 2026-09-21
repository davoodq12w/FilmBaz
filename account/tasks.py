import requests
from celery import shared_task
from django.core.mail import send_mail
from film.models import Movie
from django.db.models import Count
from account.models import UserRecommendation, FilmBazUser
from decouple import config

filmbaz_email = config("FILMBAZ_EMAIL")


@shared_task(queue="default")
def send_confirm_email(username, email):
    """
    sending confirmation email for creating user ticket.
    run with celery worker
    """
    message = f" عزیز از بازخورد شما ممنونیم{username} \n\n \n با تشکر , فیمباز "
    send_mail(
        subject="ارسال تیکت موفقیت آمیز بود",
        message=message,
        from_email=filmbaz_email,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task(queue="default")
def send_reset_password_email(email, token, uid):
    """
    sending reset password email for reset password requste.
    run with celery worker.
    """
    message = f"\ntoken = {token}\n\nuid = {uid}\n"
    send_mail(
        subject="reset password",
        message=message,
        from_email=filmbaz_email,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task()
def get_recommendation_movies():
    """
    sending request to ml_service to get movie recommendations for users.
    run with celery beat.
    """

    # get 100 of most popular movies
    popular_movies = Movie.objects.annotate(popularity=Count("interactions")).order_by("-popularity")[:100]
    movie_ids = [m.id for m in popular_movies]

    url = f"http://ml_service:8002/recomendation/get_movies/"

    # send request for active users
    # is better than request when home page load. lesser request to ml_service
    for user in FilmBazUser.objects.all():
        if user.interactions.count() < 30:
            continue

        data = {
            "user_id": user.id,
            "movie_ids": movie_ids,
        }
        response = requests.post(url, json=data)

        # if there was any error its do not save the data in DataBase
        response.raise_for_status()

        recommendations = [
            {
                "movie_id": movie_id,
                "score": score,
            }
            for movie_id, score in response.json()
        ]
        # using update_or_create becuse we need only one db record per user
        UserRecommendation.objects.update_or_create(
            user_id=user.id,
            defaults={
                "recommendations": recommendations,
            },
        )
