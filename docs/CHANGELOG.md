# **SAEP v1.0 CHANGELOG**

## 项目初始化

- Django 5.x 项目创建 + DRF + MySQL + JWT 认证
- 8 个 App 目录结构

## 用户与认证

- 自定义 User 模型（real_name、student_no、phone、student_class）
- JWT 登录 / Token 刷新 / 获取用户信息
- 5 角色 RBAC（student / evaluator / counselor / college_admin / super_admin）

## 组织架构

- College 模型 + Class 模型
- 学生 Excel 批量导入（模板下载 + 上传）
- 班级学生管理 + 测评小组配置

## 成果管理

- Achievement 模型（6 状态 + attachment + achievement_date）
- 成果 CRUD（新增/编辑/删除/详情/列表）
- 附件上传（jpg/png/pdf，UUID 文件名，10MB 限制）
- 成果提交审核（draft → submitted）

## 审核流程

- 两阶段审核：测评小组 → 辅导员
- 审核通过/退回/驳回（score + comment）
- 审核记录（AuditRecord）完整时间线
- 退回结论：测评小组退回→draft，辅导员退回→draft

## 测评与分类

- 测评批次 CRUD
- 成果分类 CRUD
- 分类筛选 + 搜索

## 公示管理

- PublicNotice 模型（draft → published → closed）
- 公示生成/发布/结束

## 成绩统计

- ScoreSummary 模型（总分 + 排名）
- 竞赛排名法（同分同排名 1,2,2,4）
- 我的成绩 + 班级排行榜
- Excel 导出（成绩 + 成果）

## 通知公告

- Announcement 模型
- 发布通知 + 列表查看

## 操作日志

- OperationLog 模型（auth/review/export 自动记录）
- 登录日志 + 审核日志 + 导出日志

## 前端

- Vue3 + TypeScript + Vite + Element Plus + Pinia
- 10 个页面：登录、Dashboard、成果列表/表单、审核、公示、成绩、排行榜
- 附件上传/预览、确认弹窗、loading 状态、空状态

------

## 统计数据

- 51 TASK
- 31 API 端点
- 11 数据模型
- 8 前端页面
- 137 测试用例
- 32 数据库迁移

------

**v1.0 — 51/51 TASK — 137 tests**
