from __future__ import annotations

from django.http import JsonResponse
from app.core.redisclient import RedisClient


def user_session_middleware(get_response):
    def middleware(request):
        session_id = request.COOKIES.get("user_session_id")
        if session_id:
            redis_key = f"user_session:{session_id}"
            user_id = RedisClient.get(redis_key)
            if user_id is None:
                return JsonResponse(
                    {
                        "error": "Invalid or expired session.",
                    }, status=401)
            request.cached_user_id = user_id
        return get_response(request)

    return middleware