"""
基础 Model 抽象类

所有业务 Model 统一继承 BaseModel，包含：
- id: BIGINT AUTO_INCREMENT
- created_at: 创建时间
- updated_at: 更新时间
"""

from django.db import models


class BaseModel(models.Model):
    """所有业务 Model 的抽象基类"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
