from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, ListView, View
from .forms import *
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.tasks import send_confirm_email


# Create your views here.

class UserLogin(LoginView):
    template_name = "authentication/login.html"
    form_class = LoginForm


class UserLogout(LogoutView):
    next_page = reverse_lazy("film:movies_list")


class CreateUser(FormView):
    template_name = "authentication/create_user.html"
    form_class = CreateUserForm
    success_url = reverse_lazy("film:home_page")

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
        context["user"] = self.request.user
        return context


@method_decorator(login_required(), name="dispatch")
class TicketView(FormView):
    form_class = TicketForm
    http_method_names = ["get", "post"]
    template_name = "account/profile.html"

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
        send_confirm_email.delay(
            username=self.request.user.username,
            email=self.request.user.email,
        )

    def form_valid(self, form):
        self._set_args(form)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        return redirect("account:profile")

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class UserSavesList(ListView):
    template_name = "account/saves.html"
    context_object_name = "movies"
    allow_empty = True

    def get_queryset(self):
        user = self.request.user
        return user.saves.all()
