from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import SupportSession, SupportMessage
from django.contrib.auth.mixins import LoginRequiredMixin
from .serializers import SupportSessionSerializer, SupportMessageSerializer
from django.db.models import Q
from django.views.generic import View
from django.db import transaction


class SupportSessionView(LoginRequiredMixin, View):
    model = SupportSession

    def get(self, request, *args, **kwargs):
        if request.user.is_staff and request.user.is_superuser:
            support_sessions = self.model.objects.filter(
                Q(supporter=request.user) | Q(supporter__isnull=True),
                status__in=[
                    SupportSession.Status.OPEN,
                    SupportSession.Status.PENDING,
                ]
            )
            session_serializer = SupportSessionSerializer(support_sessions, many=True)
            data = {
                "user_type": "admin",
                "ok": True,
                "sessions": session_serializer.data
            }
            return JsonResponse(data)
        else:
            support_session = self.model.objects.filter(user=request.user, status__in=[
                SupportSession.Status.OPEN,
                SupportSession.Status.PENDING,
            ]).first()

            if support_session is None:
                data = {
                    "user": request.user,
                    "supporter": None,
                    "status": SupportSession.Status.PENDING,
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

    if not (user.is_staff and user.is_superuser):
        return JsonResponse({
            "ok": False,
        })

    if support_session_id is None:
        return JsonResponse({
            "ok": False,
        })

    try:
        support_session_id = int(support_session_id)
    except (TypeError, ValueError):
        return JsonResponse({
            "ok": False,
        })

    with transaction.atomic():
        support_session = SupportSession.objects.select_for_update().filter(
            id=support_session_id,
            status__in=[SupportSession.Status.OPEN, SupportSession.Status.PENDING],
        ).first()

        if support_session is None:
            return JsonResponse({"ok": False})

        if support_session.supporter_id not in [None, user.id]:
            return JsonResponse({
                "ok": False,
            })

        support_session.supporter = request.user
        support_session.status = SupportSession.Status.OPEN
        support_session.save(update_fields=["supporter", "status"])

        SupportMessage.objects.filter(session=support_session, is_seen=False).update(is_seen=True)
        messages = SupportMessage.objects.filter(session=support_session).order_by("created_at")

        serializer = SupportMessageSerializer(messages, many=True)
        return JsonResponse({
            "user_type": "admin",
            "ok": True,
            "support_session_id": support_session.id,
            "messages": serializer.data
        })
