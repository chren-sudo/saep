"""
system 业务逻辑 — 操作日志
"""

from .models import OperationLog


def get_client_ip(request):
    """从 request 获取客户端真实 IP"""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def write_operation_log(user, request, module, action, detail=""):
    """统一日志写入 — TASK-043/044/045 共用

    异常被捕获，日志写入失败不影响业务流程。
    """
    try:
        OperationLog.objects.create(
            user=user,
            module=module,
            action=action,
            detail=detail,
            ip=get_client_ip(request),
        )
    except Exception:
        pass
