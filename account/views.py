from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, ListView, View
from .forms import *
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail


# Create your views here.

class UserLogin(LoginView):
    template_name = "authentication/login.html"
    form_class = LoginForm


class UserLogout(LogoutView):
    next_page = reverse_lazy("film:movies_list")


class CreateUser(FormView):
    template_name = "authentication/create_user.html"
    form_class = CreateUserForm
    success_url = reverse_lazy("film:movies_list")

    def _create_user(self, data):
        password = data.get('password')
        user = FilmBazUser.objects.create(username=data['username'], email=data['email'], phone=data['phone'])
        user.set_password(password)
        user.save()

    def form_valid(self, form):
        self._create_user(form.cleaned_data)
        return super().form_valid(form)


@method_decorator(login_required(), name="dispatch")
class UserProfile(View):
    http_method_names = ["get"]

    def get(self, request):
        user = request.user
        return render(request, "account/profile.html", {'user': user})

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class EditUser(UpdateView):
    template_name = "authentication/edit_user.html"
    form_class = EditUserForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("account:profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user = FilmBazUser.objects.get(id=self.request.user.id)
        except Exception as e:
            raise ValueError(f"error: {e}")

        context["user"] = user
        return context


@method_decorator(login_required(), name="dispatch")
class TicketView(FormView):
    # template_name = "account/profile.html"
    form_class = TicketForm

    def get_success_url(self):
        return reverse_lazy("account:profile")

    def _set_args(self, form):
        ticket = form.save(commit=False)
        try:
            ticket.phone = self.request.user.phone
            ticket.email = self.request.user.email
        except Exception as e:
            raise ModuleNotFoundError(f"error: {e}")
        ticket.save()
        self._send_confirm_email()

    def _send_confirm_email(self):
        message = f" عزیز از بازخورد شما ممنونیم{self.request.user.username} \n\n \n با تشکر , فیمباز "
        send_mail(
            subject="ارسال تیکت موفقیت آمیز بود",
            message=message,
            from_email="davodrashiworking@gmail.com",
            recipient_list=[self.request.user.email],
            fail_silently=False,
        )

    def form_valid(self, form):
        self._set_args(form)
        return super().form_valid(form)


@method_decorator(login_required(), name="dispatch")
class UserSavesList(ListView):
    template_name = "account/saves.html"
    context_object_name = "movies"
    allow_empty = True

    def get_queryset(self):
        user = self.request.user
        return user.saves.all()
