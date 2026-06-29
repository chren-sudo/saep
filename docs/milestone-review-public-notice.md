# **Milestone Review — 公示模块**

审查日期：2026-06-26 | 范围：TASK-028 ~ TASK-031 | 状态：**✅ PASS**

------

## 1. 模块概览

| TASK | 名称 | API |
|:---:|------|------|
| TASK-028 | 模型 | — |
| TASK-029 | 生成公示 | POST /public-notices/ |
| TASK-030 | 发布公示 | POST /public-notices/{id}/publish/ |
| TASK-031 | 结束公示 | POST /public-notices/{id}/close/ |

单元测试：16 tests OK

------

## 2. 状态机审查

```
DRAFT (0) ──publish──→ PUBLISHED (1) ──close──→ CLOSED (2)
```

| 检查项 | 结果 |
|------|:---:|
| 所有状态可达 | ✅ |
| 不可逆流转 | ✅ DRAFT→PUBLISHED→CLOSED 单向 |
| 终态不可复用 | ✅ CLOSED 后不可再操作 |
| _check_notice_status 复用 | ✅ publish + close 共用 |

------

## 3. 权限审查

| 检查项 | 结果 |
|------|:---:|
| get_permissions 统一 | ✅ create/publish/close 均 IsCounselorRole |
| get_queryset 统一 | ✅ counselor 仅看 managed_classes |
| Resource Hiding | ✅ 非管理班级 → 404 |
| 非 counselor | ✅ 403 |

------

## 4. 代码复用审查

| 组件 | 复用方式 |
|------|------|
| `_check_notice_status()` | publish + close 共用 |
| `get_queryset()` | 所有 action 共用 |
| `get_permissions()` | create/publish/close 一组 |
| `PublicNoticeSerializer` | publish/close/retrieve/list 共用 |
| `PublicNoticeWriteSerializer` | create 专用 |

**发现项目**：
- `Http404` 导入未使用（views.py L6），可清理。

------

## 5. 设计一致性审查

| 维度 | 对标模块 | 一致性 |
|------|------|:---:|
| ModelViewSet + @action | ReviewViewSet | ✅ |
| _check_notice_status | AchievementViewSet.perform_destroy | ✅ |
| save(update_fields) | ✅ |
| transaction.atomic | ✅ |
| get_queryset 按角色过滤 | AchievementViewSet | ✅ |

------

## 6. 单元测试覆盖

```
TASK-029: 7 tests (create/duplicate/permission/validation/approved_count/unique)
TASK-030: 4 tests (publish success/twice/not_counselor/check_status_helper)
TASK-031: 5 tests (close success/twice/draft/not_counselor/not_managed_class)
Total:   16 tests ✅
```

------

## 7. 结论

**✅ PASS。** 公示模块无 bug、无重复代码、权限统一、状态机完整。

### 小优化：

- 移除 `Http404` 未使用导入（views.py L6）

### 当前进度

```
31 / 51 → 61%
```

------
END
