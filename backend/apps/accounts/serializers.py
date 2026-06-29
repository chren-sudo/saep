"""
accounts 序列化器
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""

    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True, min_length=6)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("用户名或密码错误")
        if not user.is_active:
            raise serializers.ValidationError("用户已被禁用")

        attrs["user"] = user
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """刷新 Token 序列化器"""

    refresh = serializers.CharField(required=True)


class ProfileSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""

    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "real_name", "email", "phone", "student_no", "employee_no", "student_class", "status", "first_name", "last_name", "is_active", "date_joined", "roles")
        read_only_fields = fields

    def get_roles(self, obj):
        from .roles import get_user_roles
        return get_user_roles(obj)


class StudentImportSerializer(serializers.Serializer):
    """学生导入序列化器"""

    file = serializers.FileField(required=True)

    def validate_file(self, value):
        if not value.name.endswith(".xlsx"):
            raise serializers.ValidationError("仅支持 .xlsx 格式的 Excel 文件")
        return value
