from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView
from .forms import *
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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
class UserProfile(DetailView):
    template_name = "account/profile.html"
    slug_field = "username"
    model = FilmBazUser
    context_object_name = "user"


class EditUser(UpdateView):
    model = FilmBazUser
    template_name = "authentication/edit_user.html"
    form_class = EditUserForm
    slug_field = "username"

    def get_success_url(self):
        username = self.request.user.username
        pk = self.request.user.pk
        return reverse_lazy("account:profile", kwargs={"pk": pk, "username": username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user = FilmBazUser.objects.get(id=self.request.user.id)
        except Exception as e:
            raise ValueError(f"error: {e}")

        context["user"] = user
        return context

