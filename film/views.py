from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from analytics.models import Interaction
from .models import *
from django.views.generic import View
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
import hashlib
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone
from account.models import UserRecommendation
from django.db.models import Case, When, FloatField, Value


class HomePageView(View):
    """
    View used for getting data for home page
    all users acess to the view
    """

    def get(self, request, *args, **kwargs):
        """
        method used for getting data for home page.
        """

        if request.user.is_authenticated:
            # get queryset of movie by favorite user genres.
            favorite_genres = request.user.favorite_genres.all()
            if not favorite_genres.exists():
                return redirect("account:choose_favorite_genres")  # force user to choose the genres.
            else:
                by_chosen_genres = Movie.objects.filter(genres__in=favorite_genres).distinct().order_by('-rate')[:7]

            # get queryset of recommendations movies.
            rec_obj = UserRecommendation.objects.filter(user_id=request.user.id).first()
            if not rec_obj:
                recommendations = []

            else:
                recommendations_data = rec_obj.recommendations  # get movies dict
                rec_movie_ids = [item["movie_id"] for item in recommendations_data]

                # create a custom field for ordering movies by score.
                score_case = Case(
                    *[
                        When(
                            id=item["movie_id"],
                            then=Value(item["score"])
                        )
                        for item in recommendations_data
                    ],
                    output_field=FloatField()
                )  # giving every id a score in django models field then used the score for ordering.
                recommendations = (
                    Movie.objects
                    .filter(id__in=rec_movie_ids)
                    .annotate(score=score_case)  # set the field to objects.
                    .order_by("-score")  # sort by score.
                )[:7]

        else:
            by_chosen_genres = []
            recommendations = []

        new_movies = Movie.objects.order_by('-release_date')[:7]
        top_movies = Movie.objects.order_by('-rate')[:7]

        # all lists are serialized so we do not need to use HomePageOutputSerializer for respose.
        context = {
            "new_movies": new_movies,
            "top_movies": top_movies,
            "by_chosen_genres": by_chosen_genres,
            "recommendations": recommendations,
        }
        return render(request, "film/home_page.html", context)


class MoviesList(View):
    """
    View used for getting list of all movies.
    Performs filtering and ordering and caching data.
    all users access to the view.
    """
    filter_fields = ['genre_id', 'adult', 'release_date']
    ordering_fields = ['release_date', 'rate']
    cache_timeout = 60 * 15  # 15 minutes
    paginate_by = 21
    min_paginate_by = 7
    max_paginate_by = 21

    def get_cache_key(self, request):
        """
        inner method used for creating cache key with data of request.
        performs cache data for same filtering and ordering and pagination.
        """
        params = []

        for key, values in request.GET.lists():
            for value in values:
                params.append((key, value))

        # sorting valus allow us to leser cashing data if parameters in request are givin not in same order.
        params = sorted(params)

        raw_key = str(params).encode("utf-8")
        hashed_key = hashlib.sha256(raw_key).hexdigest()

        return f"movies_list_{hashed_key}"

    def get_filters(self, request):
        """
        inner method giving filters for queryset if there were valid filters.
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
        inner method giving orderings for queryset if there was valid ordering fields in request.
        """

        ordering = request.GET.get("ordering")

        if ordering and ordering.lstrip("-") in self.ordering_fields:
            return ordering

        return None

    def get_context_labels(self, request):
        """
        inner method giving data about applied filters or orderings or paginations.
        """
        adult = request.GET.get("adult")
        genre_id = request.GET.get("genre_id")
        release_date = request.GET.get("release_date")
        ordering = request.GET.get("ordering")

        # set labels for useing in template.
        # adult labels.
        if adult == "false":
            adult_label = "کودک و نوجوان"
        elif adult == "true":
            adult_label = "بزرگسال"
        else:
            adult_label = "همه"

        # genre_labels.
        genre_label = "ژانر ها"

        try:
            genre_pk = int(genre_id) if genre_id else None
        except ValueError:
            genre_pk = None

        if genre_pk:
            genre = Genre.objects.filter(id=genre_pk).first()
            if genre:
                genre_label = genre.fa_name

        # ordering labels.
        ordering_map = {
            "release_date": "قدیمی‌ترین",
            "-release_date": "جدیدترین",
            "rate": "کمترین امتیاز",
            "-rate": "بیشترین امتیاز",
        }
        ordering_label = ordering_map.get(ordering, "پیش‌فرض")

        # get  queryset of genres for using in template.
        cache_marker = object()
        genres = cache.get("genres", cache_marker)

        if genres is cache_marker:
            genres = list(Genre.objects.all())
            cache.set("genres", genres, 60 * 60)

        # get list of years for using in temlate.
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
        """
        inner method giving custom page size if its in valid range else returned default value.
        """
        try:
            page_size = int(request.GET.get("page_size", self.paginate_by))
        except ValueError:
            page_size = self.paginate_by

        return max(self.min_paginate_by, min(page_size, self.max_paginate_by))

    def paginate_movies(self, request, movies):
        """
        inner method giving query set of movies in requested page & paginator object & page size.
        if page number value is not valid its returned page 1.
        if page number out of range its returned last page.
        """
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
        """
        method used for getting queryset of movies.
        performs filtering and ordering and caching movies list and ajax requests.
        """

        # cache
        cache_key = self.get_cache_key(request)
        # if ther was no cache for the key cache.get return object becuose we set it for get method.
        # so we use object function for that is response of get cache is an empty object or
        # is an empty queryset value for the combonations of request parameters.
        cache_marker = object()
        cached_movies = cache.get(cache_key, cache_marker)

        # if cache avalable render page
        if cached_movies is not cache_marker:
            page_obj, paginator, page_size = self.paginate_movies(request, cached_movies)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":  # ajax requests.
                html = render_to_string(
                    "ajax/movie_cards.html",
                    {"movies": page_obj},
                    request=request
                )  # change raw data to html text.

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
    """
    View used for giving all data about movie.
    Performs caching comments and caching episodes.
    all users access to the view.
    """

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        """
        method used for getting full data of a movie.
        take id and slug of movie and giving all data of movie.
        """

        # create cache key
        comments_cache_key = f"movie_comments_{pk}_{slug}"
        episodes_cache_key = f"movie_episodes_{pk}_{slug}"
        context = {}
        # try to get cached data
        try:

            # get or set comments cache
            cached_comments = cache.get(comments_cache_key)

            movie = Movie.objects.get(pk=pk, slug=slug)
            context["movie"] = movie

            if cached_comments:
                context["comments"] = cached_comments
            else:
                comments = Comment.objects.filter(movie__slug=slug, movie__id=pk)
                context["comments"] = comments
                cache.set(comments_cache_key, comments)

            # get or set episodes cache if the movie is serie.
            if movie.is_serie:
                cached_episodes = cache.get(episodes_cache_key)
                if cached_episodes:
                    context["episodes"] = cached_episodes
                else:
                    episodes = MovieEpisode.objects.filter(movie__slug=slug, movie__id=pk).order_by("season", "episode")
                    context["episodes"] = episodes
                    cache.set(episodes_cache_key, episodes)

            # if user is loged in create a VIEW interaction
            # and find the unwatched episode for him
            if request.user.is_authenticated:
                Interaction.objects.create(
                    user=request.user,
                    movie=context["movie"],
                    interaction_type=Interaction.Type.VIEW,
                    weight=0.2
                )

                # last watch episode used for find the unwatched episode.
                last_watch = WatchProgress.objects.filter(
                    episode__movie__slug=slug,
                    episode__movie__id=pk,
                    user=request.user,
                    completed=True,
                ).order_by("-episode__season", "-episode__episode").first()

                if last_watch is not None:
                    unwatched_episode = last_watch.episode.get_next_episode()
                else:
                    unwatched_episode = movie.episodes.filter(season=1, episode=1).first()
            else:
                unwatched_episode = movie.episodes.filter(season=1, episode=1).first()

            # unwatched episode shows bellow the detail of movie in template
            # so if movie is not serie un unwatched episode allways be the main file.
            # and if movie is a serie and
            # if user is new or is not logged in unwatched episode be the first episode of serie.
            context["unwatched_episode"] = unwatched_episode

        except Exception as e:
            print(f"error in MovieDetail : {e}")

        return render(request, "film/movie_detail.html", context)


@method_decorator(login_required(), name="dispatch")
class CommentView(View):
    """
    View used for adding new comments for a movie.
    only authenticated users can add new comments.
    """
    http_method_names = ['post']

    def post(self, request):
        """
        method used for creating new comment.
        take movie id and comment text and add a new comment to the movie.
        """
        user = request.user
        movie_id = request.POST.get("movie_id")
        text = request.POST.get("text")

        if not movie_id or not text:
            return redirect("film:home_page")

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return redirect("film:home_page")

        comment = Comment.objects.create(
            movie=movie,
            user=user,
            text=text
        )

        Interaction.objects.create(
            user=request.user,
            movie=movie,
            interaction_type=Interaction.Type.COMMENT,
            weight=0.5
        )

        return render(request, "ajax/add_comment.html", {"comment": comment})

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


class SearchMovie(View):
    """
    View used for searching movies.
    all users access to the view.
    """
    http_method_names = ["get", "post"]

    # Install pg_trgm in your PostgreSQL database before using trigram search.

    def get(self, request):
        """
        method used for searching page and HTTP request.
        take text of query and give the results of text.
        """
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
        """
        method used for inline search and AJAX request.
        take text of query and give the title of results for text.
        """
        try:
            query = request.POST.get("query")
        except Exception as e:
            raise ValueError(f"error : {e}")

        movie_result = self._get_results(query)

        movie_names = [movie.fa_title for movie in movie_result][:6]
        context = {
            'movie_names': movie_names,
        }

        if request.user.is_authenticated:
            # create an interaction between user and most similar movie to query
            try:
                Interaction.objects.create(
                    user=request.user,
                    movie=Movie.objects.get(fa_title=movie_names[0]),
                    interaction_type=Interaction.Type.SEARCH,
                    weight=0.1
                )
            except Exception as e:
                print(f"Error in create Search Intraction : {e}")
                pass

        return render(request, "ajax/inline_search_results.html", context)

    def _get_results(self, query):
        """
        inner method used for searching in DB for similar movies to query text.
        take query and give the queryset of movies.
        """

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
    """
    View used for add or remove a movie of saved movie list fo user.
    only authenticated users access to the view.
    the view only used by AJAX request.
    """
    http_method_names = ["post"]

    def post(self, request):
        """
        add or remove movie of saved movies.
        take id and slug of movie and add or remove the movie.
        """
        slug = request.POST.get('slug')
        pk = request.POST.get("pk")
        user = request.user
        movie = get_object_or_404(Movie, id=pk, slug=slug)

        if movie in user.saves.all():
            user.saves.remove(movie)
            is_save = False
            try:
                # delete the SAVE interaction between user and movie.
                intraction = Interaction.objects.get(
                    user=user,
                    movie=movie,
                    interaction_type=Interaction.Type.SAVE,
                    weight=1.5,
                )
                intraction.delete()
            except Interaction.DoesNotExist:
                pass
        else:
            user.saves.add(movie)
            is_save = True
            # create a SAVE interaction between user and movie.
            Interaction.objects.get_or_create(
                user=user,
                movie=movie,
                interaction_type=Interaction.Type.SAVE,
                weight=1.5
            )

        return JsonResponse({"is_save": is_save})

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class LikeMovieView(View):
    """
    View used for add or remove a movie of liked movie list fo user.
    only authenticated users access to the view.
    the view only used by AJAX request.
    """
    http_method_names = ['post']

    def post(self, request):
        """
        add or remove movie of liked movies.
        take id and slug of movie and add or remove the movie.
        """
        slug = request.POST.get('slug')
        pk = request.POST.get('pk')
        user = request.user
        movie = get_object_or_404(Movie, id=pk, slug=slug)

        if movie in user.likes.all():
            user.likes.remove(movie)
            is_like = False
            try:
                # delete the LIKE interaction between user and movie.
                intraction = Interaction.objects.get(
                    user=user,
                    movie=movie,
                    interaction_type=Interaction.Type.LIKE,
                    weight=1.0
                )
                intraction.delete()
            except Interaction.DoesNotExist:
                pass
        else:
            user.likes.add(movie)
            is_like = True
            # create a LIKE interaction between user and movie.
            Interaction.objects.get_or_create(
                user=user,
                movie=movie,
                interaction_type=Interaction.Type.LIKE,
                weight=1.0
            )

        return JsonResponse({"is_like": is_like})

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class WatchMovieView(View):
    """
    View used for watching an episode of movie.
    only authenticated users access to the view.
    """
    http_method_names = ['get']

    def get(self, request, pk):
        """
        method give needed data for episode.
        take id of episode of movie and giving data.
        """
        episode = get_object_or_404(MovieEpisode, id=pk)

        # get last watch position
        watch_progress = episode.watch_progress.filter(user=request.user).first()
        if watch_progress is not None:
            watch_position = watch_progress.position
        else:
            watch_position = 0

        # try to get next episode or serie
        if episode.movie.is_serie:
            next_episode = episode.get_next_episode()
        else:
            next_episode = None

        context = {"episode": episode, "watch_position": watch_position, "next_episode": next_episode}
        return render(request, "film/watch.html", context)

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


@method_decorator(login_required(), name="dispatch")
class WatchProgressView(View):
    """
    View used for save datas and events of watching movie for user.
    only authenticated users access to the view.
    the view used only by AJAX request.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        """
        method create or update watch progress of user for an episode.
        take id of episode, current_time and completed data and create or update watch progress.
        """
        watchprogress, created = WatchProgress.objects.get_or_create(user=request.user, episode_id=pk)
        position = request.POST.get("current_time")
        completed = request.POST.get("completed")

        if position and completed:  # we can use condition like this because values of variable are string.
            watchprogress.position = position

            # create an WATCH interaction between movie and user.
            Interaction.objects.get_or_create(
                user=request.user,
                movie=watchprogress.episode.movie,
                interaction_type=Interaction.Type.WATCH,
                weight=0.7,
            )
            if completed == "true":
                watchprogress.completed = True
                # create an COMPLETE interaction between movie and user.
                Interaction.objects.get_or_create(
                    user=request.user,
                    movie=watchprogress.episode.movie,
                    interaction_type=Interaction.Type.COMPLETE,
                    weight=1.2,
                )
            else:
                watchprogress.completed = False

            watchprogress.save()

            return JsonResponse({"ok": True}, status=200)
        else:
            return JsonResponse({"ok": False}, status=400)

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")


def page_not_found(request, exception):
    return render(request, "partials/not_allowed.html", status=404)
