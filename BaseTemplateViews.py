from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class BaseModelView(View):
    filter_fields = None
    ordering_fields = None
    default_ordering = None

    paginate_by = None
    page_query_param = "page"
    orphans = 0

    cache_enabled = True
    cache_timeout = 60 * 5
    cache_prefix = "bmv"

    def build_cache_key(self, request, kind, model, extra=""):

        qd = request.GET.copy()

        if self.page_query_param in qd:
            qd.pop(self.page_query_param)

        query_string = qd.urlencode()
        model_name = model._meta.label_lower if model else "no-model"
        view_name = self.__class__.__name__

        return f"{self.cache_prefix}:{kind}:{view_name}:{model_name}:{query_string}:{extra}"

    def apply_filters(self, request, qs):
        if not self.filter_fields:
            return qs

        filters = {}

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
