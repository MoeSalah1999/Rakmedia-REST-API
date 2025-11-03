import json
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response

def cache_response(prefix: str, timeout: int = 60):
    """
    Decorator to cache DRF responses safely for both class-based and function-based views.

    Works with:
        @cache_response('key')  -> on a get() method directly
        OR
        @method_decorator(cache_response('key'), name='get')
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            # Handle both (self, request, *args, **kwargs) and (request, *args, **kwargs)
            if len(args) == 0:
                raise TypeError("cache_response: view_func called with no arguments")

            # Identify self/request properly
            if hasattr(args[0], 'request'):  
                # Case 1: bound view (self)
                self = args[0]
                request = args[1] if len(args) > 1 else getattr(self, 'request', None)
            else:
                # Case 2: function-based view
                self = None
                request = args[0]

            if request is None:
                raise TypeError("cache_response: could not detect request object")

            user_id = getattr(request.user, "id", "anon")
            cache_key = f"{prefix}:{user_id}:{request.get_full_path()}"

            cached_data = cache.get(cache_key)
            if cached_data:
                print(f"[CACHE HIT] {cache_key}")
                return Response(
                    data=json.loads(cached_data["data"]),
                    status=cached_data["status"]
                )

            print(f"[CACHE MISS] {cache_key}")

            # Execute the actual view
            response = view_func(*args, **kwargs)

            # Cache only valid GET responses
            if hasattr(request, "method") and request.method == "GET" and hasattr(response, "status_code") and response.status_code == 200:
                cache.set(
                    cache_key,
                    {
                        "data": json.dumps(response.data),
                        "status": response.status_code,
                    },
                    timeout,
                )

            return response

        return _wrapped_view

    return decorator
