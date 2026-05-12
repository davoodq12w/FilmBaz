from django.http import JsonResponse
from .models import SupportSession
from BaseTemplateViews import BaseModelView
from django.contrib.auth.mixins import LoginRequiredMixin
import json


class SupportSessionView(BaseModelView, LoginRequiredMixin):
    model = SupportSession
    cache_enabled = False

    def get(self, request, *args, **kwargs):
        support_session = self.model.objects.filter(user=request.user, status__in=["Pending", "Open"]).first()

        if support_session is None:
            data = {
                "user": request.user,
                "supporter": None,
                "status": "Pending",
            }
            support_session = self.model.objects.create(**data)

        return JsonResponse({
            "ok": True,
            "support_session_id": support_session.id,
        })
