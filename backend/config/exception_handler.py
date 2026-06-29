"""
统一异常处理器

返回格式:
    成功: {"code": 0, "message": "success", "data": {...}}
    失败: {"code": xxx, "message": "...", "data": null}
"""

from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        code = _map_status_to_code(exc, response.status_code)
        message = _extract_message(exc, response)
        response.data = {
            "code": code,
            "message": message,
            "data": None,
        }

    return response


def _map_status_to_code(exc, status_code):
    """将 HTTP 状态码映射为业务 code"""
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return 401
    if isinstance(exc, PermissionDenied):
        return 403
    if isinstance(exc, NotFound):
        return 404
    if isinstance(exc, ValidationError):
        return 400
    if isinstance(exc, APIException):
        return exc.status_code
    return status_code


def _extract_message(exc, response):
    """提取错误消息"""
    if isinstance(exc, ValidationError):
        data = response.data
        if isinstance(data, dict) and "code" not in data:
            return _flatten_validation_errors(data) or str(exc)
    return str(exc.detail) if hasattr(exc, "detail") else str(exc)


def _flatten_validation_errors(data):
    """将 DRF 的字段校验错误展平为字符串"""
    messages = []
    for field, errors in data.items():
        if isinstance(errors, list):
            for err in errors:
                messages.append(f"{field}: {err}")
        else:
            messages.append(f"{field}: {errors}")
    return "; ".join(messages) if messages else ""
