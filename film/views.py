from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from .models import *
from django.views.generic import View
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
import hashlib
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string



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
    filter_fields = ['genre_id', 'adult', 'release_date']
    ordering_fields = ['release_date', 'rate']
    cache_timeout = 60 * 15  # 15 minutes
    paginate_by = 21
    min_paginate_by = 7
    max_paginate_by = 21

    def get_cache_key(self, request):
        params = []

        ignored_params = {"page", "page_size"}

        for key, values in request.GET.lists():
            if key in ignored_params:
                continue

            for value in values:
                params.append((key, value))

        params = sorted(params)

        raw_key = str(params).encode("utf-8")
        hashed_key = hashlib.sha256(raw_key).hexdigest()

        return f"movies_list_{hashed_key}"

    def get_filters(self, request):
        """
        گرفتن فیلترهای معتبر از query string
        """
        filters = {}

        for field in self.filter_fields:
            value = request.GET.get(field)

            if value in [None, ""]:
                continue

            if field == "adult":
                value = value.lower()

                if value == "true":
                    filters["adult"] = True
                elif value == "false":
                    filters["adult"] = False

            elif field == "genre_id":
                try:
                    filters["genres__id"] = int(value)
                except ValueError:
                    continue


            elif field == "release_date":
                try:
                    filters["release_date__year"] = int(value)
                except ValueError:
                    continue

        return filters

    def get_ordering(self, request):
        """
        گرفتن ordering معتبر
        """

        ordering = request.GET.get("ordering")

        if ordering and ordering.lstrip("-") in self.ordering_fields:
            return ordering

        return None

    def get_context_labels(self, request):
        adult = request.GET.get("adult")
        genre_id = request.GET.get("genre_id")
        release_date = request.GET.get("release_date")
        ordering = request.GET.get("ordering")

        if adult == "false":
            adult_label = "کودک و نوجوان"
        elif adult == "true":
            adult_label = "بزرگسال"
        else:
            adult_label = "بزرگسال"

        genre_label = "ژانر ها"

        if genre_id:
            genre = Genre.objects.filter(id=genre_id).first()
            if genre:
                genre_label = genre.fa_name

        ordering_map = {
            "release_date": "قدیمی‌ترین",
            "-release_date": "جدیدترین",
            "rate": "کمترین امتیاز",
            "-rate": "بیشترین امتیاز",
        }
        ordering_label = ordering_map.get(ordering, "پیش‌فرض")

        # get genres
        cache_marker = object()
        genres = cache.get("genres", cache_marker)

        if genres is cache_marker:
            genres = list(Genre.objects.all())
            cache.set("genres", genres, 60 * 60)

        # get_years
        years = [
            date_obj.year
            for date_obj in Movie.objects.filter(release_date__isnull=False).dates('release_date', 'year')
        ]

        return {
            "selected_genre": genre_id,
            "selected_adult": adult,
            "selected_release_date": release_date,
            "selected_ordering": ordering,
            "genre_label": genre_label,
            "adult_label": adult_label,
            "release_date_label": release_date if release_date else "سال ساخت",
            "ordering_label": ordering_label,
            "genres": genres,
            "years": years,
            "page_size_param": request.GET.get("page_size", self.paginate_by),
        }

    def get_page_size(self, request):
        try:
            page_size = int(request.GET.get("page_size", self.paginate_by))
        except ValueError:
            page_size = self.paginate_by

        return max(self.min_paginate_by, min(page_size, self.max_paginate_by))

    def paginate_movies(self, request, movies):
        page_size = self.get_page_size(request)
        page_number = request.GET.get("page", 1)

        paginator = Paginator(movies, page_size)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return page_obj, paginator, page_size

    def get(self, request, *args, **kwargs):

        # cache
        cache_key = self.get_cache_key(request)
        cache_marker = object()
        cached_movies = cache.get(cache_key, cache_marker)

        # if cache avalable render page
        if cached_movies is not cache_marker:
            page_obj, paginator, page_size = self.paginate_movies(request, cached_movies)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                html = render_to_string(
                    "ajax/movie_cards.html",
                    {"movies": page_obj},
                    request=request
                )

                return JsonResponse({
                    "html": html,
                    "has_next": page_obj.has_next(),
                    "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                })

            context = {
                "movies": page_obj,
                "page_obj": page_obj,
                "paginator": paginator,
                "page_size": page_size,
            }
            context.update(self.get_context_labels(request))

            return render(request, "film/movies_list.html", context)

        # get base qs
        movies = Movie.objects.all()

        # get filters
        filters = self.get_filters(request)

        # applay filters
        if filters:
            movies = movies.filter(**filters)

        # get ordering
        ordering = self.get_ordering(request)

        # applay ordering
        if ordering:
            movies = movies.order_by(ordering)

        movies = list(movies)

        page_obj, paginator, page_size = self.paginate_movies(request, movies)

        # if request is AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "ajax/movie_cards.html",
                {"movies": page_obj},
                request=request
            )

            return JsonResponse({
                "html": html,
                "has_next": page_obj.has_next(),
                "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            })

        # set new cache
        cache.set(cache_key, movies, timeout=self.cache_timeout)

        # create context
        context = {
            "movies": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "page_size": page_size,
        }
        # add labels for context
        context.update(self.get_context_labels(request))

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

        movie_names = [movie.fa_title for movie in movie_result][:6]
        context = {
            'movie_names': movie_names,
        }
        return render(request, "ajax/inline_search_results.html", context)

    def _get_results(self, query):

        try:
            result1 = Movie.objects.annotate(similarity=TrigramSimilarity("fa_title", query)).filter(similarity__gt=0.1)
            result2 = Movie.objects.annotate(similarity=TrigramSimilarity("orj_title", query)).filter(
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
