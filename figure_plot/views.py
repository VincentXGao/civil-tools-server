from django.http import JsonResponse
import json


def simple_api(request):
    data = {"message": "Hello, this is a simple API!", "status": "success"}
    return JsonResponse(data)


def shear_mass_ratio(request):
    if request.method == "POST":
        try:
            # 获取 POST 请求中的 JSON 数据
            data = json.loads(request.body)
            name = data.get("name")
            if name:
                response_data = {"message": f"Hello, {name}!"}
                return JsonResponse(response_data)
            else:
                return JsonResponse({"error": 'Missing "name" field'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
