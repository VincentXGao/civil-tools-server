import json
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse


def check_post_data(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            # 获取 POST 请求中的 JSON 数据
            data = json.loads(request.body)
            data = data.get("data")
            if data:
                return func(self, request, *args, **kwargs)
            else:
                return Response(
                    {"error": 'Missing "data" field'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

    return wrapper


def check_post_data_specific_field(field: str):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            try:
                # 获取 POST 请求中的 JSON 数据
                data = json.loads(request.body)
                data = data.get(field)
                if data:
                    return func(self, request, *args, **kwargs)
                else:
                    return Response(
                        {"error": f'Missing "{field}" field'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
                )

        return wrapper

    return decorator
