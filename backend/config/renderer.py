"""
统一响应渲染器

确保所有成功响应格式为:
    {"code": 0, "message": "success", "data": {...}}

已包装的响应（如分页、异常处理）不会被重复包装。
"""

from rest_framework.renderers import JSONRenderer


class StandardRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if response is not None and 200 <= response.status_code < 300:
            # 已含 "code" 的不重复包装（分页、异常处理等）
            if isinstance(data, dict) and "code" in data:
                return super().render(data, accepted_media_type, renderer_context)
            # 包装成功响应
            data = {"code": 0, "message": "success", "data": data}

        return super().render(data, accepted_media_type, renderer_context)
