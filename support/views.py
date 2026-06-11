from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import SupportSession, SupportMessage
from django.contrib.auth.mixins import LoginRequiredMixin
from .serializers import SupportSessionSerializer, SupportMessageSerializer
from django.db.models import Q
from django.views.generic import View


class SupportSessionView(View, LoginRequiredMixin):
    model = SupportSession

    def get(self, request, *args, **kwargs):
        if request.user.is_staff and request.user.is_superuser:
            support_sessions = self.model.objects.filter(
                Q(supporter=request.user) | Q(supporter__isnull=True),
                status__in=["Pending", "Open"]
            )
            session_serializer = SupportSessionSerializer(support_sessions, many=True)
            data = {
                "user_type": "admin",
                "ok": True,
                "sessions": session_serializer.data
            }
            return JsonResponse(data)
        else:
            support_session = self.model.objects.filter(user=request.user, status__in=["Pending", "Open"]).first()

            if support_session is None:
                data = {
                    "user": request.user,
                    "supporter": None,
                    "status": "Pending",
                }
                support_session = self.model.objects.create(**data)

            messages = SupportMessage.objects.filter(session=support_session).order_by("created_at")
            message_serializer = SupportMessageSerializer(messages, many=True)

            return JsonResponse({
                "user_type": "user",
                "ok": True,
                "support_session_id": support_session.id,
                "messages": message_serializer.data
            })


@login_required()
def get_support_session_for_admin(request, support_session_id=None):
    user = request.user
    if not user.is_superuser:
        return JsonResponse({
            "ok": False,
        })

    if support_session_id is None:
        return JsonResponse({
            "ok": False,
        })

    support_session = get_object_or_404(SupportSession, id=support_session_id)
    messages = SupportMessage.objects.filter(session=support_session).order_by("created_at")

    for message in messages:
        message.is_seen = True
        message.save()

    serializer = SupportMessageSerializer(messages, many=True)
    return JsonResponse({
        "user_type": "admin",
        "ok": True,
        "support_session_id": support_session.id,
        "messages": serializer.data
    })
