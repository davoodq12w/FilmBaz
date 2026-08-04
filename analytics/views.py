from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from film.models import Movie, MovieEpisode
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required(), name="dispatch")
class ShareIntractionView(View):
    http_method_names = ['post']

    def post(self, request):
        slug = request.POST.get("slug")
        pk = request.POST.get("pk")
        movie = get_object_or_404(Movie, pk=pk, slug=slug)
        user = request.user

        Interaction.objects.get_or_create(
            user=user,
            movie=movie,
            interaction_type=Interaction.Type.SHARE,
            defaults={"weight": 1.2}
        )

        return None

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "partials/not_allowed.html")
