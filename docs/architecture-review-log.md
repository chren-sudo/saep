# **Milestone-1 — 成果管理模块**

审查日期：2026-06-22 | 状态：✅ PASS

审查报告：[milestone-review-achievement-module.md](milestone-review-achievement-module.md)

## 范围

TASK-001 ~ TASK-017，涵盖：项目初始化、认证、RBAC、组织架构、学生导入、测评批次 CRUD、成果分类 CRUD、成果 CRUD。

## 审查结果

| 类别 | 检查项 | 结果 |
|------|:---:|:---:|
| 状态机一致性 | 6 Status 定义 + 编辑/删除规则 | ✅ 零差异 |
| 权限矩阵 | 5 角色 × 5 接口 | ✅ 零差异 |
| Serializer 安全性 | 5 字段保护 | ✅ 不可伪造 |
| API 文档一致性 | README + api-design vs code | ✅ 同步 |
| 未来兼容性 | TASK-018/019/020 | ✅ 无阻塞 |
| 技术债 | 7 项 | 均为低~中风险 |

## 决策

✅ Milestone-1 通过。允许进入 TASK-018。

------

# **架构审查日志**

记录各 TASK 的架构决策、争议点和最终结论。

------

# **TASK-013 — 成果新增接口**

审查日期：2026-06-22 | 轮次：1 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | student/class_obj 填充策略 | 服务端强制注入，客户端不可传入 |
| 2 | batch 有效性校验 | 仅 status=1(RUNNING) 可提交 |
| 3 | achievement_date 范围校验 | 须在 batch.start_time ~ batch.end_time 之间 |
| 4 | 创建状态 | 仅创建 draft，不创建 submitted |
| 5 | 附件支持 | multipart/form-data，内置类型校验 |
| 6 | 权限 | 仅 student 角色 |

## 争议点

- **附件是否应现在实现**：决定现在就支持 multipart，避免 TASK-018 重构 Serializer 签名
- **是否应同时支持直接 submitted**：决定仅 draft，两步提交流程分阶段实现

## 最终模型

```
Serializer: AchievementWriteSerializer (fields: batch, category, title, 
            achievement_date, level, description, attachment)
自动注入:  student, class_obj, status=draft
权限级:    IsStudentRole (permissions.py 新增)
```

------

# **TASK-014 — 成果列表接口**

审查日期：2026-06-22 | 轮次：2 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | 角色数据范围 | student(自己) / evaluator+counselor(本班) / admin(全部) |
| 2 | college_admin 归属 | 暂同 super_admin，后续通过 User.college 细化 |
| 3 | 筛选参数 | status / batch / class_obj / category |
| 4 | 搜索 | keyword → title |
| 5 | 性能优化 | select_related(student, category, batch) |
| 6 | 列表 Serializer | 精简版（不含 description/attachment） |

## 争议点

- **college_admin 缺少 college 归属**：讨论新增 User.college FK（TASK-013.5），决定暂缓到学院统计模块上线前统一设计
- **使用 `batch` 而非 `batch_id`**：DRF filterset_fields 使用 Django 字段名，确认为 `batch`

## 最终模型

```
ViewSet:    get_queryset() 按角色控制数据范围
Serializer: AchievementListSerializer（9 个展示字段，不含长文本和附件）
Filters:    status / batch / class_obj / category
Search:     title
```

------

# **TASK-016 — 成果编辑接口**

审查日期：2026-06-22 | 轮次：3 轮

## 第一轮 — 基础设计

| # | 决策 | 结论 |
|---|------|------|
| 1 | 可编辑状态 | draft / rejected |
| 2 | 禁止编辑状态 | submitted / reviewing / counselor_reviewing / approved |
| 3 | 权限 | 仅 student 本人 |
| 4 | 编辑不改变 status | 保留原状态，由"重新提交"动作独立处理 |

## 第二轮 — 字段冻结规则

| # | 决策 | 结论 |
|---|------|------|
| 1 | rejected 可否改 batch | ❌ 不可。防跨批次数据漂移，AuditRecord 上下文错误 |
| 2 | batch 永久只读？ | draft 可改，rejected 及以后不可 |
| 3 | PUT vs PATCH | 同时支持，推荐 PATCH |
| 4 | 字段白名单 | student/class_obj/status/score/submitted_at 永久只读 |

## 第三轮 — 字段区分与实现方案

| # | 决策 | 结论 |
|---|------|------|
| 1 | rejected 可否改 category | ✅ 可以。不影响 AuditRecord 一致性 |
| 2 | validate_batch 在 PATCH 下有无漏洞 | 无。字段级 validate 不传不触发，validate() 中 attrs.get() 正确回退 |
| 3 | 业务规则集中化 | 统一在 Serializer.validate() 中处理，禁止分散到各 validate_xxx() |

## 争议点

- **rejected 改 batch vs 改 category**：batch 改会导致跨批次漂移（冻结），category 无结构性风险（允许）
- **Validate 逻辑放在哪**：经历三轮讨论，从 `validate_batch()` 移至 `validate()` 统一处理

## 最终编辑字段矩阵

```
              draft    rejected   submitted+
batch         ✅       ❌         ❌
category      ✅       ✅         ❌
title         ✅       ✅         ❌
achievement_date ✅    ✅         ❌
level         ✅       ✅         ❌
description   ✅       ✅         ❌
attachment    ✅       ✅         ❌
───────────────────────────────────────
student       ⛔       ⛔         ⛔
class_obj     ⛔       ⛔         ⛔
status        ⛔       ⛔         ⛔
score         ⛔       ⛔         ⛔
submitted_at  ⛔       ⛔         ⛔
```

## 最终模型

```
Serializer: WriteSerializer.validate() 集中处理:
            → 状态校验 (draft/rejected 可编辑)
            → rejected 禁止改 batch
            → achievement_date vs batch 时间范围
权限:       IsStudentRole (create + update + partial_update)
```

------

## 通用决策模式

从以上三次审查中提炼的设计原则：

1. **on_delete 优先 PROTECT** — 有引用时禁止删除，宁可手动处理也不静默级联
2. **字段冻结优先于开放** — 不确定是否可改的字段先冻结，后续按需解冻
3. **业务规则集中在 validate()** — 单一入口，可读性优先于"语义字段方法"
4. **先审查后编码** — 每次设计至少 2-3 轮审查，检查与后续 TASK 的衔接

------

END

------

# **TASK-017 — 成果删除接口**

审查日期：2026-06-22 | 轮次：1 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | 可删除状态 | draft / rejected |
| 2 | 禁止删除状态 | submitted / reviewing / counselor_reviewing / approved |
| 3 | super_admin 权限 | 无特殊豁免，同样受状态规则限制 |
| 4 | 权限 | 仅 student 本人（IsStudentRole） |
| 5 | 删除方式 | 物理删除 |

## 技术债

### AuditRecord CASCADE 与 rejected 删除

- **现状**：AuditRecord.achievement FK = CASCADE。删除 rejected 成果 → 级联删除关联 AuditRecord。
- **影响**：被驳回成果的审核评论、分数快照全部丢失。
- **缓解**：OperationLog（TASK-042）记录"谁在何时删除了哪个成果"。
- **计划**：V2.0 如需保留审核轨迹，将 FK 改为 PROTECT（阻止删除有 AuditRecord 的 rejected 成果）或 SET_NULL。
- **标记**：TASK-019 实现时将 FK 明确标注为 CASCADE，并在注释中说明此技术债。

------

# **TASK-019 技术债说明**

## Achievement ← AuditRecord CASCADE

```python
# apps/achievements/models.py — AuditRecord (TASK-019)
achievement = models.ForeignKey(
    Achievement,
    on_delete=models.CASCADE,  # 技术债：删除 rejected 成果时审核记录丢失
    related_name="audit_records",
)
```

标记位置：TASK-019 models.py 注释中注明此技术债。

------

# **TASK-018 — 附件上传**

审查日期：2026-06-22 | 轮次：1 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | 存储路径 | uploads/%Y/%m/{uuid}.{ext} |
| 2 | UUID 文件名 | 避免同名冲突（Django 默认已处理，UUID 更可控） |
| 3 | 文件白名单 | .jpg/.jpeg/.png/.pdf（不含 doc/docx） |
| 4 | 文件大小 | 10MB（settings.FILE_UPLOAD_MAX_SIZE） |
| 5 | attachment_url | 使用 obj.attachment.url |

## 技术债

- **旧附件不自动删除**：更新 attachment 时旧文件保留在磁盘，长期积累占用空间。V2.0 可增加更新时删除旧文件逻辑或定时清理任务。

------


------

# **TASK-019 — AuditRecord 模型**

审查日期：2026-06-22 | 轮次：2 轮

## 关键决策

| # | 决策 | R1 | R2 |
|---|------|:---:|:---:|
| 1 | reviewer FK | CASCADE | **SET_NULL** |
| 2 | reviewer_name 快照 | — | **新增** |
| 3 | score 类型 | FloatField | **DecimalField(5,2)** |
| 4 | FK 索引 | 手动 indexes | **删除，用Django默认** |
| 5 | ordering | created_at | **保持升序** |
| 6 | status_before/after | — | **V2.0 技术债** |
| 7 | Achievement.score | — | **保持 FloatField，TASK-033 评估** |

## 技术债

- achievement FK CASCADE: 删除 rejected → 审核轨迹丢失
- status_before/after: V2.0 增加状态变更快照
- Achievement.score FloatField: TASK-033 评估是否需要改为 Decimal

------

------

# **TASK-020 — 待审核列表**

审查日期：2026-06-25 | 轮次：Final Review

## Final Review 决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | reviewing 状态 | 枚举保留，MVP 不经过，V2.0 审核锁定预留 |
| 2 | evaluator approve | submitted → counselor_reviewing（一步，不经过 reviewing） |
| 3 | counselor return | counselor_reviewing → submitted（回到 evaluator 重新审） |
| 4 | stage 参数 | 移除，角色自动确定审核阶段 |
| 5 | ViewSet | ListModelMixin + GenericViewSet（仅 list） |
| 6 | 班级归属 | evaluator→student_class, counselor→managed_classes（一一对应，不用 or 短路） |
| 7 | has_attachment | 新增，审核人可快速判断是否有证明材料 |

## MVP 最终状态机

```
draft → 学生提交 → submitted → evaluator通过 → counselor_reviewing → counselor通过 → approved
              ↑                      │                           │
              │                      │ evaluator退回             │
              └──────────────────────┘                           │
                                                                 │
                    counselor退回 ──────────────────────────────┘
```

## 技术债

- TECH-DEBT-008: reviewing 状态审核锁定机制（V2.0）
- reviewing 状态在代码枚举中存在但 MVP 不经过

------

------

# **TASK-021 — 审核通过接口**

审查日期：2026-06-25 | 轮次：Final Review

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | score 必填 | required=True |
| 2 | 班级权限 | get_queryset() 统一过滤，不在范围 → 404 |
| 3 | transaction.atomic | 必须使用 |
| 4 | Achievement.score 同步 | approve 时同步更新 |
| 5 | reviewer_name 快照 | 创建时写入 |
| 6 | 重复 approve 防护 | 状态变更后 get_queryset 自然排除 → 404 |

## 权限策略

审核模块统一："看不到 = 不存在 = 404"

------


------

# **TASK-022 — 审核退回接口**

审查日期：2026-06-25 | 轮次：1 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | url_path | "return" |
| 2 | comment | required=True, allow_blank=False |
| 3 | Achievement.score | 不修改 |
| 4 | AuditRecord.score | null |
| 5 | 权限 | get_queryset() 统一过滤 → 404 |

------

# **TASK-023 — 审核驳回接口**

审查日期：2026-06-25 | 轮次：1 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | rejected 为终态 | 不可审核、不可编辑、不可重新提交 |
| 2 | comment | required=True, allow_blank=False |
| 3 | Achievement.score | 不修改 |
| 4 | AuditRecord.score | null |
| 5 | 权限 | get_queryset() 统一过滤 → 404 |
| 6 | url_path | "reject" |

## rejected 终态规则

- 学生不可编辑
- 学生不可重新提交
- 审核人不可再次 approve / return / reject
- 仅允许 student 本人删除（TASK-017）

------

------

# **TASK-024 — 审核日志查询**

审查日期：2026-06-25 | 轮次：1 轮

## 关键决策

| # | 决策 | 结论 |
|---|------|------|
| 1 | 不新增 ViewSet | AchievementViewSet @action (detail=True, url_path="audit-records") |
| 2 | 权限复用 | AchievementViewSet.get_queryset() → 看不到成果=看不到轨迹 |
| 3 | Serializer 简化 | 无 nested reviewer/status，reviewer_name 快照 |
| 4 | 排序 | created_at 升序（审核时间线从早到晚） |

------

# **Milestone-2 — 审核流程模块**

审查日期：2026-06-25 | 状态：✅ PASS

审查报告：[milestone-review-review-module.md](milestone-review-review-module.md)

5 API + 31 单元测试 + 完整状态机 + 统一 404 权限策略。无阻塞问题。

------

------

# **TECH-DEBT-010 — college_admin 缺少学院归属**

发现日期：2026-06-26 | 严重度：中

## 现状
- User 模型无 `college` FK 字段
- Class 已有关联 College（Class.college）
- college_admin 无法确定所属学院

## 当前缓解
- college_admin 暂与 super_admin 保持一致，可访问全部数据
- AchievementViewSet、ClassStudentViewSet、EvaluatorViewSet 均采用此策略

## 推荐方案
```python
# User 新增:
college = ForeignKey("organizations.College", SET_NULL, null=True, blank=True, related_name="admins")
```

## 修改范围
- 仅修改 `_get_managed_class()` 一处即可完成学院级权限收敛
- 各 ViewSet 无需修改
- 建议在 TASK-036（统计排名）之前作为独立 TASK 实施

------

------

# **TASK-027 — 辅导员审核**

审查日期：2026-06-26 | 类型：**零代码验证**

TASK-027 要求的 counselor approve/return/reject 已在 TASK-021~023 中作为 `_check_review_permission()` 的 counselor 分支实现。回归测试 21/21 OK。TASK-027 不新增代码。

------

------

# **Milestone — 公示模块**

审查日期：2026-06-26 | 范围：TASK-028 ~ TASK-031 | 状态：✅ PASS

审查报告：[milestone-review-public-notice.md](milestone-review-public-notice.md)

PublicNotice: DRAFT → PUBLISHED → CLOSED。16 tests OK。无阻塞问题。

------

------

# **TASK-039 — 通知查询**

审查日期：2026-06-26 | 类型：**零代码验证**

GET /announcements 列表和详情已在 TASK-038 的 ListModelMixin + RetrieveModelMixin 中实现。无需新增代码。

------

------

# **REQ-001 — 学生查看全班排名权限**

提出日期：2026-06-26 | 状态：⏳ 待实施

## 需求
学生应该能看到本班所有同学的成绩排名（公平公正公开原则）。

## 影响范围
- GET /scores/ranking/?batch=3：当前 student 分支只返回自己，需改为返回本班全部
- GET /scores/me：保持不变（自己的成绩明细）

## 实施位置
`_get_score_queryset()`: student 分支从 `qs.filter(student=user)` 改为 `qs.filter(student__student_class=user.student_class)`

## 建议时机
TASK-036 回归测试时一并实施，或在 TASK-047（Dashboard）开发前统一调整。

------
