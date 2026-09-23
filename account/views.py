from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, ListView, View
from .forms import *
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.tasks import send_confirm_email
from film.models import Genre, Movie


class UserLogin(LoginView):
    """
    View for user loging in
    all users access to this view
    """
    template_name = "authentication/login.html"
    form_class = LoginForm


class UserLogout(LogoutView):
    """
    View for user loging out
    only authenticated users access to view
    """
    next_page = reverse_lazy("film:home_page")


class CreateUser(FormView):
    """
    View used for creating user.
    user loged in after creation.
    all users access to the view
    """
    template_name = "authentication/create_user.html"
    form_class = CreateUserForm
    success_url = reverse_lazy("film:home_page")

    def _create_user(self, data):
        """
        inner method for creation user by django orm
        """
        password = data.get('password')  # get password for set hashed password
        user = FilmBazUser.objects.create(username=data['username'], email=data['email'], phone=data['phone'])
        user.set_password(password)  # set hashed password
        user.save()
        return user

    def form_valid(self, form):
        data = form.cleaned_data
        self._create_user(data)

        # checking the username and password match or not.
        # if match retured user object else returned None
        user = authenticate(
            self.request,
            username=data["username"],
            password=data["password"],
        )

        # loging the user after creations
        if user is not None:
            login(self.request, user)

        return super().form_valid(form)


@method_decorator(login_required(), name="dispatch")
class UserProfile(View):
    """
    View used for giving the data of users
    only authenticated users access to the view
    """
    http_method_names = ["get"]

    def get(self, request):
        """
        getting user object
        """
        user = request.user
        return render(request, "account/profile.html", {'user': user})

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        managing the not allowed method in View
        """
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class EditUser(UpdateView):
    """
    View used for changing the users detials
    only authenticated users access to the view
    """
    template_name = "authentication/edit_user.html"
    form_class = EditUserForm

    def get_object(self, queryset=None):
        """
        giving the authenticated user object
        """
        return self.request.user

    def get_success_url(self):
        """
        giving the redirect url (profile) after chaging the user details successfuly.
        """
        return reverse_lazy("account:profile")

    def get_context_data(self, **kwargs):
        """
        add user to the context for access to user object in template.
        """
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@method_decorator(login_required(), name="dispatch")
class TicketView(FormView):
    """
    View user for creating new ticket for users
    only authenticated users access to the view
    """
    form_class = TicketForm
    http_method_names = ["get", "post"]
    template_name = "account/profile.html"

    def get_success_url(self):
        """
        giving redirect url (profile) after creating new ticket successfuly.
        """
        return reverse_lazy("account:profile")

    def _set_args(self, form):
        """
        inner method for creating ticket object and send email conformation.
        """
        ticket = form.save(commit=False)
        try:
            ticket.phone = self.request.user.phone
            ticket.email = self.request.user.email
        except Exception as e:
            raise ModuleNotFoundError(f"error: {e}")
        ticket.save()

        # sending an email with Celery
        # so that the task runs in the background and does not interfere with the method's work
        send_confirm_email.delay(
            username=self.request.user.username,
            email=self.request.user.email,
        )

    def form_valid(self, form):
        """
        calling the custome method for do custome works.
        """
        self._set_args(form)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        """
        for creating tickets we need to go to profile page.
        """
        return redirect("account:profile")

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        managing not allowed methods.
        """
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class UserSavesList(ListView):
    """
    View used for giving the saved movies of user.
    only authenticated users access to the view.
    """
    template_name = "account/saves.html"
    context_object_name = "movies"
    allow_empty = True

    def get_queryset(self):
        """
        returned all saved movies by users
        """
        user = self.request.user
        return user.saves.all()


@method_decorator(login_required(), name="dispatch")
class UserLikesList(ListView):
    """
    View used for giving the liked movies of user.
    only authenticated users access to the view.
    """
    template_name = "account/likes.html"
    context_object_name = "movies"
    allow_empty = True

    def get_queryset(self):
        """
        returned all liked movies by users
        """
        user = self.request.user
        return user.likes.all()


@method_decorator(login_required(), name="dispatch")
class UserFavoriteGenres(View):
    """
    View used for giving and changing favorite genres list of user.
    only authenticated users access to the view.
    """
    http_method_names = ["get", "post"]

    def get(self, request):
        """
        getting list of favorite genres of user.
        """
        user = request.user
        initial_data = {
            "genres": user.favorite_genres.all()
        }

        # giving base data to form
        form = FavoriteGenresForm(initial=initial_data)

        # getting queryset of gernres from form
        genres_qs = form.fields["genres"].queryset

        # get list of BoundWidget objects of genres like this bllow
        # [
        #   < BoundWidget(Action) >,
        #   < BoundWidget(Comedy) >,
        #   < BoundWidget(Drama) >,
        # ]
        chechboxes = list(form["genres"])

        # merging checkboxes and gernes with zip method then we got a data like this bllow
        # (
        #     (Genre(Action), Checkbox(Action)),
        #     (Genre(Comedy), Checkbox(Comedy)),
        #     (Genre(Drama), Checkbox(Drama)),
        # )
        genres_with_cb = zip(genres_qs, chechboxes)

        context = {
            "form": form,
            "genres_with_cb": genres_with_cb,
        }
        return render(request, "account/choose_favorite_genres.html", context)

    def post(self, request):
        """
        changing list of favorite genres of user.
        """
        user = request.user

        # fill the form with requested data
        form = FavoriteGenresForm(request.POST)

        genres_qs = form.fields["genres"].queryset
        chechboxes = list(form["genres"])
        genres_with_cb = zip(genres_qs, chechboxes)

        if form.is_valid():
            genres = form.cleaned_data["genres"]

            # use set method for replace data
            user.favorite_genres.set(genres)
            user.save()
            return redirect("film:home_page")

        # if data not valid we return the old data
        form.initial["genres"] = user.favorite_genres.all()
        context = {
            "form": form,
            "genres_with_cb": genres_with_cb,
        }
        return render(request, "account/choose_favorite_genres.html", context)
