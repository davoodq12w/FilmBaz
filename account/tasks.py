from celery import shared_task
from django.core.mail import send_mail


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
