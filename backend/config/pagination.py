"""
统一分页类

返回格式:
    {
        "code": 0,
        "message": "success",
        "data": {
            "results": [...],
            "total": 156,
            "page": 1,
            "page_size": 20
        }
    }
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "results": data,
                    "total": self.page.paginator.count,
                    "page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                },
            }
        )
