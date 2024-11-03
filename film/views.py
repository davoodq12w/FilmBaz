from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.views.generic import ListView, DetailView, View
from django.contrib.postgres.search import TrigramSimilarity


# Create your views here.

class MoviesList(ListView):
    template_name = "film/movies_list.html"
    model = Movie
    context_object_name = "movies"
    allow_empty = True

class MovieDetail(DetailView):
    template_name = "film/movie_detail.html"
    context_object_name = "movie"
    model = Movie
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = Movie.objects.get(id=self.kwargs["pk"])
        context["comments"] = Comment.objects.filter(movie=movie)
        return context


@method_decorator(login_required(), name="dispatch")
class CommentView(View):
    http_method_names = ['post']

    def post(self, request):
        user = request.user
        movie = Movie.objects.get(id=request.POST.get("movie_id"))
        text = request.POST.get("text")
        comment = Comment.objects.create(movie=movie, user=user, text=text)
        comment.save()
        return render(request, "ajax/add_comment.html", {"comment": comment})

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


class SearchMovie(View):
    http_method_names = ["get", "post"]

    # ⚠️ don't forget: install the pg-trgm in your postgres database.

    def get(self, request):

        try:
            query = request.GET.get("query")
        except Exception as e:
            raise ValueError(f"error : {e}")

        movie_result = self._get_results(query)

        context = {
            "query": query,
            "movie_result": movie_result,
        }
        return render(request, "film/search_results.html", context)

    def post(self, request):

        try:
            query = request.POST.get("query")
        except Exception as e:
            raise ValueError(f"error : {e}")

        movie_result = self._get_results(query)

        movie_names = [movie.title for movie in movie_result][:6]
        context = {
            'movie_names': movie_names,
        }
        return render(request, "ajax/inline_search_results.html", context)

    def _get_results(self, query):

        try:
            result1 = Movie.objects.annotate(similarity=TrigramSimilarity("title", query)).filter(similarity__gt=0.1)
            result2 = Movie.objects.annotate(similarity=TrigramSimilarity("english_title", query)).filter(
                similarity__gt=0.1)

            movie_result = (result1 | result2).order_by("-similarity")
        except Exception as e:
            raise ValueError(f"error: {e}")
        return movie_result

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class SaveMovieView(View):
    http_method_names = ["post"]

    def post(self, request):
        slug = request.POST.get('slug')
        pk = request.POST.get("pk")
        user = request.user
        try:
            movie = Movie.objects.get(pk=pk, slug=slug)
        except Exception as e:
            raise ModuleNotFoundError(f"error: {e}")

        try:
            if movie in user.saves.all():
                user.saves.remove(movie)
                is_save = False
            else:
                user.saves.add(movie)
                is_save = True
        except Exception as e:
            raise ValueError(f"error {e}")

        return JsonResponse({"is_save": is_save})

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


def page_not_found(request, exception):
    return render(request, "partials/not_allowed.html", status=404)
