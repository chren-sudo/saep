# **开发任务清单**

版本：MVP V1.0

说明：

```text
每个 TASK 开发前先阅读 docs/CLAUDE.md 及对应设计文档。

涉及接口的 TASK 标注了关联路径，开发时对照 docs/api-design.md。

禁止跳跃开发，按 TASK 编号顺序推进。
```

------

# **第一阶段：项目初始化**

## **TASK-001**

创建Django项目

涉及：

```text
项目骨架 / config / apps 目录
```

验收：

```text
□ python manage.py runserver 能启动
□ MySQL 连接成功
□ DRF 已配置
□ 8 个 apps 目录已创建
```

------

## **TASK-002**

配置JWT认证

涉及接口：

```text
POST /auth/login      登录
POST /auth/refresh    刷新Token
GET /auth/profile     获取当前用户
```

验收：

```text
□ 登录成功，返回 access + refresh
□ Token 刷新成功
□ 携带 Token 请求 /auth/profile 返回用户信息
□ 未携带 Token 返回 401
```

------

## **TASK-003**

初始化RBAC权限体系

涉及：

```text
Django Group / Permission
```

角色：

```text
student
evaluator
counselor
college_admin
super_admin
```

验收：

```text
□ 5 个 Group 创建成功
□ 权限矩阵生效（对照 docs/api-design.md 角色×接口权限矩阵）
□ 提供初始化脚本（management command）
```

------

# **第二阶段：组织架构**

## **TASK-004**

创建College模型

涉及：

```text
organizations.College
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ 字段：name / code（unique）
```

------

## **TASK-005**

创建Class模型

涉及：

```text
organizations.Class
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ 字段：college / name / grade / counselor
□ on_delete 策略正确（college CASCADE，counselor SET_NULL）
```

------

## **TASK-006**

扩展User模型

涉及：

```text
accounts.User（继承 AbstractUser）
```

验收：

```text
□ Model 完成
□ 迁移成功
□ 新增字段：real_name / student_no / employee_no / phone / avatar / status
□ AUTH_USER_MODEL 已配置
```

------

## **TASK-007**

学生导入功能

涉及接口：

```text
POST /students/import   Excel导入
```

验收：

```text
□ 支持 Excel 导入（OpenPyXL）
□ 导入时自动创建 User 并分配 student 角色
□ 导入失败行有错误提示
□ 重复学号跳过并记录
```

------

# **第三阶段：测评管理**

## **TASK-008**

测评批次模型

涉及：

```text
evaluations.EvaluationBatch
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ status 使用 IntegerChoices（0/1/2）
```

------

## **TASK-009**

测评批次CRUD

涉及接口：

```text
GET    /batches        列表
POST   /batches        新增
GET    /batches/{id}   详情
PUT    /batches/{id}   编辑
DELETE /batches/{id}   删除
```

验收：

```text
□ 5 个接口可用
□ 权限：college_admin / super_admin 可操作
□ 分页参数生效
```

------

## **TASK-010**

成果分类模型

涉及：

```text
achievements.AchievementCategory
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ 字段：name / sort_order
```

------

## **TASK-011**

成果分类CRUD

涉及接口：

```text
GET    /categories        列表
POST   /categories        新增
PUT    /categories/{id}   编辑
DELETE /categories/{id}   删除
```

验收：

```text
□ 4 个接口可用
□ 删除时校验是否被成果引用（PROTECT）
□ 权限：college_admin / super_admin 可操作
```

------

# **第四阶段：成果申报**

## **TASK-012**

Achievement模型

涉及：

```text
achievements.Achievement
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ status 使用 TextChoices（6 个状态）
□ ForeignKey 的 on_delete 与 related_name 符合 docs/django-models-design.md
```

------

## **TASK-013**

成果新增接口

涉及接口：

```text
POST /achievements
```

验收：

```text
□ 接口可用，返回 id + status=draft
□ 权限：仅 student
□ Serializer 校验必填字段
□ 新增时自动填入 student_id、class_id
```

------

## **TASK-014**

成果列表接口

涉及接口：

```text
GET /achievements
```

验收：

```text
□ 接口可用，返回分页结构（results/total/page/page_size）
□ 支持 keyword / status / batch_id 筛选
□ 权限：按角色返回不同数据范围（自己/本班/本学院/全部）
```

------

## **TASK-015**

成果详情接口

涉及接口：

```text
GET /achievements/{id}
```

验收：

```text
□ 接口可用，返回完整字段（含嵌套 student/category/batch）
□ 权限：按角色校验数据范围
```

------

## **TASK-016**

成果修改接口

涉及接口：

```text
PUT /achievements/{id}
```

验收：

```text
□ 接口可用
□ 仅 status=draft 或 status=rejected 可编辑
□ 权限：仅 student 本人
```

------

## **TASK-017**

成果删除接口

涉及接口：

```text
DELETE /achievements/{id}
```

验收：

```text
□ 接口可用
□ 仅 status=draft 或 status=rejected 可删（可删除状态白名单）
□ 权限：student 本人 / super_admin
□ 其余状态删除返回 400
```

------

## **TASK-018**

附件上传功能

涉及接口：

```text
POST /uploads   文件上传
```

验收：

```text
□ 接口可用，返回文件路径
□ 文件类型校验：仅允许 jpg / jpeg / png / pdf
□ 禁止类型：zip / rar / exe / bat / js
□ 上传目录：media/uploads/%Y/%m/
□ 文件大小限制生效
```

------

# **第五阶段：审核流程**

## **TASK-019**

AuditRecord模型

涉及：

```text
achievements.AuditRecord
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ review_stage / action 使用 TextChoices
□ ForeignKey 的 related_name='audit_records'
```

------

## **TASK-020**

待审核列表

涉及接口：

```text
GET /reviews
```

验收：

```text
□ 接口可用，返回分页结构
□ 支持 stage 筛选（evaluator / counselor）
□ 权限：evaluator 看第一阶段待审，counselor 看第二阶段待审
```

------

## **TASK-021**

审核通过接口

涉及接口：

```text
POST /reviews/{id}/approve
```

验收：

```text
□ 接口可用
□ 状态流转正确：
   MVP: evaluator approve: submitted → counselor_reviewing
   MVP: counselor approve: counselor_reviewing → approved
□ 写入 AuditRecord（含 review_stage / score / comment）
□ 权限：按当前状态判断操作人角色
□ 非法状态转换返回 400
```

------

## **TASK-022**

审核退回接口

涉及接口：

```text
POST /reviews/{id}/return
```

验收：

```text
□ 接口可用
□ 状态流转正确：
   第一阶段：reviewing → draft（退回学生）
   第二阶段：counselor_reviewing → reviewing（退回测评小组）
□ 写入 AuditRecord
□ 权限：按当前状态判断操作人角色
```

------

## **TASK-023**

审核驳回接口

涉及接口：

```text
POST /reviews/{id}/reject
```

验收：

```text
□ 接口可用
□ 状态流转正确：任意阶段 → rejected（终态）
□ 写入 AuditRecord
□ 权限：按当前状态判断操作人角色
□ rejected 状态不可再审核
```

------

## **TASK-024**

审核日志查询

涉及接口：

```text
GET /achievements/{id}/audit-records
```

验收：

```text
□ 接口可用，返回该成果的审核轨迹
□ 按时间倒序排列
□ 包含 reviewer / review_stage / action / score / comment
```

------

# **第六阶段：辅导员管理**

## **TASK-025**

测评小组配置

涉及接口：

```text
GET    /class/evaluators    查看本班测评小组
POST   /class/evaluators    添加测评小组成员
DELETE /class/evaluators/{id}  移除成员
```

验收：

```text
□ 接口可用
□ 权限：仅 counselor 可操作本班
□ 添加时自动分配 evaluator 角色
□ 移除时撤销 evaluator 角色
```

------

## **TASK-026**

班级学生管理

涉及接口：

```text
GET /class/students   查看本班学生
```

验收：

```text
□ 接口可用
□ 权限：counselor 看本班，college_admin 看本学院
□ 支持分页与关键字搜索
```

------

## **TASK-027**

辅导员审核

涉及接口：

```text
POST /reviews/{id}/approve   第二阶段
POST /reviews/{id}/return    第二阶段
POST /reviews/{id}/reject    第二阶段
```

验收：

```text
□ 仅 status=counselor_reviewing 时 counselor 可操作
□ 状态流转正确（对照 system-design.md 状态转换表）
□ 与 TASK-021~023 共用审核逻辑，通过 review_stage 区分
```

------

# **第七阶段：公示管理**

## **TASK-028**

PublicNotice模型

涉及：

```text
publicity.PublicNotice
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ status 使用 IntegerChoices（0/1/2）
```

------

## **TASK-029**

生成公示

涉及接口：

```text
POST /public-notices
```

验收：

```text
□ 接口可用
□ 自动拉取该批次该班 status=approved 的成果
□ 生成公示记录，status=0（草稿）
□ 权限：仅 counselor
```

------

## **TASK-030**

发布公示

涉及接口：

```text
POST /public-notices/{id}/publish
```

验收：

```text
□ 接口可用
□ status：0 → 1（公示中）
□ 设置 start_time / end_time
□ 权限：仅 counselor
```

------

## **TASK-031**

结束公示

涉及接口：

```text
POST /public-notices/{id}/close
```

验收：

```text
□ 接口可用
□ status：1 → 2（已结束）
□ 权限：仅 counselor
□ 公示结束后触发成绩汇总（关联 TASK-033）
```

------

# **第八阶段：统计模块**

## **TASK-032**

ScoreSummary模型

涉及：

```text
statistics.ScoreSummary
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ unique_together: (student, batch)
□ 联合索引 (student, batch)
```

------

## **TASK-033**

成绩汇总逻辑

涉及：

```text
统计逻辑（非接口，由公示结束触发或手动触发）
```

验收：

```text
□ 汇总指定批次 + 班级下所有 approved 成果的 score 之和
□ 写入 score_summaries.total_score
□ 幂等：重复执行不产生重复记录
```

------

## **TASK-034**

排名计算逻辑

涉及：

```text
统计逻辑（非接口）
```

验收：

```text
□ 按班级内 total_score 降序计算 ranking
□ 同分同排名（标准竞赛排名法）
□ 更新 score_summaries.ranking
```

------

## **TASK-035**

我的成绩接口

涉及接口：

```text
GET /scores/me
```

验收：

```text
□ 接口可用
□ 返回当前用户指定批次的 total_score / ranking
□ 支持 batch_id 筛选
□ 权限：student / evaluator
```

------

## **TASK-036**

班级排名接口

涉及接口：

```text
GET /scores/ranking
```

验收：

```text
□ 接口可用，返回分页结构
□ 按班级内 ranking 升序排列
□ 支持 batch_id / class_id 筛选
□ 权限：counselor 看本班，college_admin 看本学院，super_admin 看全部
```

------

# **第九阶段：通知模块**

## **TASK-037**

Announcement模型

涉及：

```text
notifications.Announcement
```

验收：

```text
□ Model 完成，继承 BaseModel
□ 迁移成功
□ 字段：title / content / publisher
```

------

## **TASK-038**

通知发布

涉及接口：

```text
POST /announcements
```

验收：

```text
□ 接口可用
□ 权限：college_admin / super_admin
□ publisher 自动填入当前用户
```

------

## **TASK-039**

通知查询

涉及接口：

```text
GET /announcements
```

验收：

```text
□ 接口可用，返回分页结构
□ 所有人可查看
□ 支持关键字搜索
```

------

# **第十阶段：导出模块**

## **TASK-040**

成绩Excel导出

涉及接口：

```text
GET /export/scores
```

验收：

```text
□ 接口可用，返回 Excel 文件
□ 使用 OpenPyXL
□ 支持 batch_id / class_id 筛选
□ 权限：counselor / college_admin / super_admin
□ 导出后写入 operation_logs
```

------

## **TASK-041**

成果Excel导出

涉及接口：

```text
GET /export/achievements
```

验收：

```text
□ 接口可用，返回 Excel 文件
□ 使用 OpenPyXL
□ 支持 batch_id / status 筛选
□ 权限：counselor / college_admin / super_admin
□ 导出后写入 operation_logs
```

------

# **第十一阶段：系统模块**

## **TASK-042**

OperationLog模型

涉及：

```text
system.OperationLog
```

验收：

```text
□ Model 完成（不继承 BaseModel，仅 created_at）
□ 迁移成功
□ module 使用 TextChoices
```

------

## **TASK-043**

登录日志

涉及：

```text
记录登录操作到 operation_logs
```

验收：

```text
□ 登录成功后自动写入日志
□ 记录：user / module=auth / action=login / ip
```

------

## **TASK-044**

审核日志

涉及：

```text
记录审核操作到 operation_logs
```

验收：

```text
□ 审核（approve/return/reject）后自动写入日志
□ 记录：user / module=review / action=审核动作 / ip
```

------

## **TASK-045**

导出日志

涉及：

```text
记录导出操作到 operation_logs
```

验收：

```text
□ 导出后自动写入日志
□ 记录：user / module=export / action=导出类型 / ip
```

------

# **第十二阶段：前端开发**

## **TASK-046**

登录页

涉及：

```text
/login
```

验收：

```text
□ 页面渲染正常
□ 登录成功跳转 Dashboard
□ 登录失败有错误提示
□ Token 存储到 Pinia
```

------

## **TASK-047**

Dashboard

涉及：

```text
/dashboard
```

验收：

```text
□ 展示当前测评批次
□ 展示待审核数量
□ 展示已通过数量
□ 展示公示状态
```

------

## **TASK-048**

成果管理页面

涉及：

```text
/achievement/list   成果列表
/achievement/create 新增成果
```

验收：

```text
□ 列表支持分页、筛选、状态标签
□ 新增表单字段完整
□ 支持保存草稿 / 提交审核
□ 附件上传功能正常
```

------

## **TASK-049**

审核页面

涉及：

```text
/review/list   待审核列表
/review/detail 审核详情
```

验收：

```text
□ 列表按阶段筛选
□ 详情页展示成果信息 + 附件预览
□ 通过/退回/驳回按钮可用
□ 评分与意见填写
```

------

## **TASK-050**

公示页面

涉及：

```text
/notice   公示管理
```

验收：

```text
□ 生成公示功能可用
□ 发布公示功能可用
□ 结束公示功能可用
```

------

## **TASK-051**

统计页面

涉及：

```text
/my-score      我的成绩
/statistics    学院统计
```

验收：

```text
□ 我的成绩展示总分与排名
□ 学院统计展示班级数量/学生数量/成果数量/平均分
□ 排行榜展示正确
```

------

# **MVP完成标准**

全部任务完成：

```text
TASK-001 → TASK-051
```

即达到V1.0上线标准。

每个 TASK 完成后须满足 docs/CLAUDE.md 的 Definition of Done：

```text
□ 数据库迁移完成
□ Model完成
□ Serializer完成
□ API完成
□ 权限校验完成
□ 操作日志完成
□ 前端页面完成（后端阶段可跳过此项）
□ 本地测试通过
□ 无明显Bug
```

END
