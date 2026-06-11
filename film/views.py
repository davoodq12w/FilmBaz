from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.views.generic import View
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache


class HomePageView(View):
    def get(self, request, *args, **kwargs):
        new_movies = Movie.objects.order_by('-release_date')[:7]
        top_movies = Movie.objects.order_by('-rate')[:7]

        context = {
            "new_movies": new_movies,
            "top_movies": top_movies,
        }
        return render(request, "film/home_page.html", context)


class MoviesList(View):
    filter_fields = ['genre_id', 'adult', 'is_serie', 'country', 'year']
    ordering_fields = ['release_date', 'rate']
    paginate_by = 20

    def get(self, request, *args, **kwargs):

        query_string = request.META.get("QUERY_STRING", "")
        cache_key = f"movies_list_{query_string}"  # create cache key

        # try to get cached data
        try:
            cache_movies = cache.get(cache_key)
            if cache_movies:
                context = {"movies": cache_movies}
                return render(request, "film/movies_list.html", context)

            # if cached data is not avalable
            # get query set of movies
            movies = Movie.objects.all()

            # aplly ordering
            ordering = request.GET.get("ordering", None)

            if ordering:
                if ordering.lstrip("-") in self.ordering_fields:
                    movies = movies.order_by(ordering)

            # set cache
            cache.set(cache_key, movies)
        except Exception as e:
            print(f"error in MoviesListView : {e}")

        context = {"movies": movies}
        return render(request, "film/movies_list.html", context)


class MovieDetail(View):

    def get(self, request, pk=None, slug=None, *args, **kwargs):

        # create cache key
        movie_cache_key = f"movie_detail_{pk}_{slug}"
        comments_cache_key = f"movie_comments_{pk}_{slug}"
        context = {}
        # try to get cached data
        try:
            cached_movie = cache.get(movie_cache_key)
            cached_comments = cache.get(comments_cache_key)

            if cached_movie:
                context["movie"] = cached_movie
            else:
                movie = Movie.objects.get(pk=pk, slug=slug)
                context["movie"] = movie
                cache.set(movie_cache_key, movie)

            if cached_comments:
                context["comments"] = cached_comments
            else:
                comments = Comment.objects.filter(movie__slug=slug, movie__id=pk)
                context["comments"] = comments
                cache.set(comments_cache_key, comments)

        except Exception as e:
            print(f"error in MovieDetail : {e}")

        return render(request, "film/movie_detail.html", context)


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
