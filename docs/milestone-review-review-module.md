# **Milestone-2 Review — 审核流程模块**

审查日期：2026-06-25 | 范围：TASK-020 ~ TASK-024 | 状态：**✅ PASS**

------

## 1. Milestone 概览

| 指标 | 值 |
|------|------|
| 范围 | TASK-020 待审核列表 ~ TASK-024 审核日志 |
| 交付 API | 5 个 |
| 新增模型 | AuditRecord (TASK-019) |
| 单元测试 | 31 个 |
| 状态 | ✅ PASS |

------

## 2. 已完成 TASK 列表

| TASK | 名称 | 交付物 |
|:---:|------|------|
| TASK-020 | 待审核列表 | GET /reviews/ |
| TASK-021 | 审核通过 | POST /reviews/{id}/approve/ |
| TASK-022 | 审核退回 | POST /reviews/{id}/return/ |
| TASK-023 | 审核驳回 | POST /reviews/{id}/reject/ |
| TASK-024 | 审核日志 | GET /achievements/{id}/audit-records/ |

------

## 3. API 清单

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/reviews/` | evaluator/counselor | 待审列表（角色自动确定阶段） |
| POST | `/api/v1/reviews/{id}/approve/` | evaluator/counselor | 通过（score 必填） |
| POST | `/api/v1/reviews/{id}/return/` | evaluator/counselor | 退回（comment 必填） |
| POST | `/api/v1/reviews/{id}/reject/` | evaluator/counselor | 驳回（comment 必填） |
| GET | `/api/v1/achievements/{id}/audit-records/` | 所有已认证角色 | 审核时间线 |

------

## 4. 状态机验证

### MVP 状态流转

```
draft ──提交──→ submitted ──evaluator approve──→ counselor_reviewing ──counselor approve──→ approved
                                  │                      │
                          evaluator return          counselor return
                              → draft                   → submitted
                                  │                      │
                          evaluator reject          counselor reject
                              → rejected               → rejected
```

| 检查项 | 结果 |
|------|:---:|
| 6 状态全部定义 | ✅ |
| 4 种审核动作全部覆盖 | ✅ approve / return / reject × 2 阶段 |
| 终态不可逆 | ✅ approved / rejected |
| reviewing 预留 | ✅ 枚举存在，MVP 不经过 |
| 状态转换无遗漏 | ✅ |

------

## 5. 权限模型验证

| 检查项 | 结果 |
|------|:---:|
| evaluator 仅本班 | ✅ get_queryset → class_obj=student_class |
| counselor 仅管理班级 | ✅ get_queryset → class_obj__in=managed_classes |
| 非审核角色 → 404 | ✅ get_queryset → qs.none() |
| 不在阶段 → 404 | ✅ status 不匹配 → get_queryset 排除 |
| 统一 404 策略 | ✅ "看不到 = 不存在" |
| 无 403 混用 | ✅ PermissionDenied 仅在 _check_review_permission 兜底 |

------

## 6. AuditRecord 设计验证

| 检查项 | 结果 |
|------|:---:|
| approve 写入 | ✅ action=approve, score=传入值 |
| return 写入 | ✅ action=return, score=null |
| reject 写入 | ✅ action=reject, score=null |
| reviewer_name 快照 | ✅ 三种动作均写入 |
| transaction.atomic | ✅ 三种动作均包装 |
| Achievement.score 仅 approve 修改 | ✅ return/reject 不修改 |
| TASK-024 查询 | ✅ achievement.audit_records.all() ← created_at 升序 |

------

## 7. 单元测试汇总

```
TASK-020 test_review_list       5 tests ✅
TASK-021 test_review_approve    7 tests ✅
TASK-022 test_review_return     6 tests ✅
TASK-023 test_review_reject     8 tests ✅
TASK-024 test_audit_records_api 5 tests ✅
────────────────────────────────────────
Total                          31 tests ✅
```

------

## 8. Postman/Apifox 验证汇总

| TASK | 关键场景 | 结果 |
|:---:|------|:---:|
| TASK-020 | evaluator 看本班 submitted / counselor 看本班 counselor_reviewing / student 空 | ✅ |
| TASK-021 | evaluator approve→counselor_reviewing / counselor approve→approved / score 必填 / 重复 reject | ✅ |
| TASK-022 | evaluator return→draft / counselor return→submitted / comment 必填 / score 不变 | ✅ |
| TASK-023 | evaluator reject→rejected / counselor reject→rejected / comment 必填 / score 不变 | ✅ |
| TASK-024 | 审核轨迹返回 / 空数组 / 升序 | ✅ |

------

## 9. 已知技术债

| # | 技术债 | 影响 | 计划 |
|:---:|------|------|------|
| TECH-DEBT-008 | reviewing 审核锁定机制 | 多 evaluator 并发 | V2.0 |
| TECH-DEBT-009 | 并发审核行锁 | 同上 | V2.0 |
| — | AuditRecord CASCADE | 删除 rejected 丢失审核记录 | V2.0 |
| — | status_before/after | 审核轨迹不显式展示状态变更 | V2.0 |
| — | Achievement.score FloatField | 精度 | TASK-033 评估 |

------

## 10. 检查清单

| # | 检查项 | 结果 |
|:---:|------|:---:|
| 1 | Achievement.score 仅 approve 修改 | ✅ |
| 2 | return/reject 不修改 score | ✅ |
| 3 | AuditRecord 覆盖 approve/return/reject | ✅ |
| 4 | 权限统一为"看不到=404" | ✅ |
| 5 | 文档同步 | ✅ |
| 6 | 无遗留 TODO 阻塞后续开发 | ✅ |
| 7 | 无阻塞性问题 | ✅ |

------

## 结论

**✅ Milestone-2 PASS**

审核流程模块（TASK-020 ~ TASK-024）已完成，5 个 API 全部可用，31 个单元测试全部通过，状态机完整，权限统一，允许进入 TASK-025。

------

END
