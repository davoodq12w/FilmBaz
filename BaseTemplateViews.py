from django.views import View
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Case, When
from django.core.cache import cache


class BaseModelView(View):
    model = None
    filter_fields = None
    ordering_fields = None
    default_ordering = None

    paginate_by = None
    page_query_param = "page"
    orphans = 0

    cache_enabled = True
    cache_timeout = 60 * 5
    cache_prefix = "bmv"

    def _build_cache_key(self, request, kind, custom_model=None, extra=""):
        if custom_model is None:
            model = self.model
        else:
            model = custom_model

        qd = request.GET.copy()

        if self.page_query_param in qd:
            qd.pop(self.page_query_param)

        query_string = qd.urlencode()
        model_name = model._meta.label_lower if model else "no-model"
        view_name = self.__class__.__name__

        return f"{self.cache_prefix}:{kind}:{view_name}:{model_name}:{query_string}:{extra}"

    def get_base_queryset(self, custom_model=None):
        if custom_model is None:
            model = self.model
        else:
            model = custom_model

        if model is None:
            raise ValueError("model باید در کلاس فرزند مقداردهی شود")
        return model.objects.all()

    def apply_filters(self, request, qs):
        if not self.filter_fields:
            return qs

        filters = {}

        if isinstance(self.filter_fields, dict):
            for param_name, lookup_expr in self.filter_fields.items():
                value = request.GET.get(param_name)
                if value not in (None, ""):
                    filters[lookup_expr] = value

        else:
            for f in self.filter_fields:
                value = request.GET.get(f)
                if value not in (None, ""):
                    filters[f] = value

        return qs.filter(**filters) if filters else qs

    def apply_ordering(self, request, qs):
        ordering = request.GET.get("ordering")
        if ordering:
            field = ordering.lstrip("-")
            if self.ordering_fields and field in self.ordering_fields:
                return qs.order_by(ordering)
            return qs

        if self.default_ordering:
            return qs.order_by(self.default_ordering)

        return qs

    def get_queryset(self, request, custom_model=None):
        if custom_model is None:
            model = self.model
        else:
            model = custom_model

        if self.cache_enabled:
            key = self._build_cache_key(request, custom_model=custom_model, kind="qs")
            cached_ids = cache.get(key)
            if cached_ids is not None:
                if not cached_ids:
                    return model.objects.none()
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(cached_ids)])
                base_qs = self.get_base_queryset(custom_model=custom_model)
                return base_qs.filter(pk__in=cached_ids).order_by(preserved)

        qs = self.get_base_queryset(custom_model=custom_model)
        qs = self.apply_filters(request, qs)
        qs = self.apply_ordering(request, qs)

        if self.cache_enabled:
            ids = list(qs.values_list("pk", flat=True))
            cache.set(key, ids, timeout=self.cache_timeout)

        return qs

    def paginate_queryset(self, request, qs):
        if not self.paginate_by:
            return None, None

        paginator = Paginator(qs, self.paginate_by, orphans=self.orphans)
        page_number = request.GET.get(self.page_query_param, 1)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        pagination = {
            "page": page_obj.number,
            "per_page": self.paginate_by,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
        return page_obj, pagination

    def get_object(self, custom_model=None, pk=None, *args, **kwargs):
        if custom_model is None:
            model = self.model
        else:
            model = custom_model

        if pk is None:
            raise ValueError("مقدار pk ضروری است.")

        if self.cache_enabled:
            key = f"{self.cache_prefix}:obj:{self.__class__.__name__}:{model.__name__}:{pk}"
            cached_obj = cache.get(key)
            if cached_obj is not None:
                return cached_obj

        obj = get_object_or_404(model, pk=pk)

        if self.cache_enabled:
            cache.set(key, obj, timeout=self.cache_timeout)

        return obj
