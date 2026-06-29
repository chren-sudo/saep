# **api-design.md**

# **REST API设计文档**

Base URL：

```text
/api/v1
```

认证方式：

```text
JWT Bearer Token
```

------

# **通用约定**

## **统一返回格式**

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

说明：

`code` 为 0 表示成功，非 0 表示失败（与 HTTP 状态码配合使用）。

## **分页参数（所有列表接口统一）**

```text
page        页码，默认 1

page_size   每页条数，默认 20，最大 100
```

## **分页返回结构**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "results": [],
    "total": 156,
    "page": 1,
    "page_size": 20
  }
}
```

## **筛选参数传值规则**

```text
status     传字符串枚举值（draft / submitted / reviewing / ...）

batch_id   传数字

class_id   传数字

keyword    传字符串（模糊匹配标题）
```

## **时间格式**

统一 ISO 8601：

```text
2026-06-18T10:30:00Z
```

------

# **Auth**

## 登录

```http
POST /auth/login
```

请求：

```json
{
  "username":"admin",
  "password":"123456"
}
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access": "jwt-token",
    "refresh": "refresh-token"
  }
}
```

------

## 刷新 Token

```http
POST /auth/refresh
```

请求：

```json
{
  "refresh": "refresh-token"
}
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access": "new-jwt-token"
  }
}
```

------

## 获取当前用户

```http
GET /auth/profile
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "real_name": "",
    "email": "admin@saep.local",
    "phone": "",
    "student_no": "",
    "employee_no": "",
    "student_class": null,
    "status": true,
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "date_joined": "2026-06-18T10:00:00Z",
    "roles": ["super_admin"]
  }
}
```

------

# **Health**

## 健康检查

```http
GET /health
```

权限：无需认证

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

------

# **学生模块**

## 下载导入模板

```http
GET /students/template
```

权限：college_admin / super_admin

返回：Excel .xlsx 文件

------

## 批量导入学生

```http
POST /students/import
```

权限：college_admin / super_admin

请求：`multipart/form-data`，字段 `file`（.xlsx）

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 8,
    "success": 2,
    "skipped": 6,
    "errors": [
      {"row": 4, "student_no": "20250003", "detail": "班级不存在"},
      {"row": 5, "student_no": "", "detail": "学号为空"}
    ]
  }
}
```

导入逻辑：
- username = 学号，默认密码 = 学号后6位
- 自动分配 student 角色
- 自动绑定 student_class
- 学院不存在、班级不存在、学号重复 → 跳过并记录错误

------

# **批次模块**

## 批次列表

```http
GET /batches
```

查询参数：page、page_size、status（0/1/2）、search（名称关键词）

权限：college_admin / super_admin

返回：分页结构

------

## 新增批次

```http
POST /batches
```

权限：college_admin / super_admin

请求：

```json
{
  "name": "2026年度综合测评",
  "description": "面向全体本科生...",
  "start_time": "2026-06-01T00:00:00Z",
  "end_time": "2026-10-01T00:00:00Z"
}
```

说明：新增默认 status=0（未开始），不接受客户端传入。

------

## 批次详情

```http
GET /batches/{id}
```

权限：college_admin / super_admin

------

## 编辑批次

```http
PUT /batches/{id}
```

权限：college_admin / super_admin

请求：同新增，部分字段可选。

------

## 删除批次

```http
DELETE /batches/{id}
```

权限：college_admin / super_admin

说明：Achievement 引用后由数据库 PROTECT 保护。

------

# **分类模块**

## 分类列表

```http
GET /categories
```

权限：college_admin / super_admin

返回：分页结构，按 sort_order 升序。

------

## 新增分类

```http
POST /categories
```

权限：college_admin / super_admin

请求：

```json
{
  "name": "创新创业",
  "sort_order": 6
}
```

说明：name 唯一，重复返回 400。

------

## 分类详情

```http
GET /categories/{id}
```

权限：college_admin / super_admin

------

## 编辑分类

```http
PUT /categories/{id}
```

权限：college_admin / super_admin

------

## 删除分类

```http
DELETE /categories/{id}
```

权限：college_admin / super_admin

说明：被 Achievement 引用后由数据库 PROTECT 保护。

------

# **成果模块**

## **成果列表**

```http
GET /achievements
```

查询参数：

```text
page          页码，默认 1
page_size     每页条数，默认 20
keyword       关键字搜索（匹配标题）
status        状态筛选（draft/submitted/reviewing/counselor_reviewing/approved/rejected）
batch_id      批次筛选
```

权限：

```text
student       仅返回自己的成果
evaluator     返回本班成果
counselor     返回本班成果
college_admin 返回本学院成果
super_admin   返回全部
```

请求示例：

```http
GET /achievements?page=1&page_size=20&status=submitted&batch_id=3&keyword=竞赛
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "results": [
      {
        "id": 101,
        "title": "全国大学生数学建模竞赛一等奖",
        "category": { "id": 1, "name": "学科竞赛" },
        "level": "国家级",
        "score": 8.5,
        "status": "submitted",
        "submitted_at": "2026-06-18T10:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

------

## **新增成果**

```http
POST /achievements
```

权限：

```text
student
```

请求：

```json
{
  "batch_id": 3,
  "category_id": 1,
  "title": "全国大学生数学建模竞赛一等奖",
  "level": "国家级",
  "description": "2026年全国大学生数学建模竞赛获一等奖",
  "attachment": "uploads/2026/06/xxx.pdf"
}
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 101,
    "status": "draft"
  }
}
```

说明：

新增默认状态为 draft（草稿），需学生主动提交审核。

------

## **成果详情**

```http
GET /achievements/{id}
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 101,
    "student": { "id": 1, "real_name": "张三", "student_no": "2026001" },
    "class": { "id": 5, "name": "计算机1班" },
    "batch": { "id": 3, "name": "2026年度综合测评" },
    "category": { "id": 1, "name": "学科竞赛" },
    "title": "全国大学生数学建模竞赛一等奖",
    "level": "国家级",
    "description": "2026年全国大学生数学建模竞赛获一等奖",
    "attachment": "uploads/2026/06/3cb482e9f516438da3f792a7758255a8.pdf",
    "attachment_url": "/media/uploads/2026/06/3cb482e9f516438da3f792a7758255a8.pdf",
    "score": 8.5,
    "status": "approved",
    "submitted_at": "2026-06-18T10:30:00Z",
    "created_at": "2026-06-18T10:00:00Z",
    "updated_at": "2026-06-19T15:00:00Z"
  }
}
```

------

## **编辑成果**

```http
PUT /achievements/{id}
```

权限：

```text
student 仅可编辑自己 status=draft 或 status=rejected 的成果
```

请求：同新增，部分字段可选更新。

返回：同新增返回。

说明：

非 draft / rejected 状态禁止编辑。

------

## **编辑成果**

```http
PUT /achievements/{id}
PATCH /achievements/{id}
```

权限：

```text
student 仅可编辑自己 status=draft 或 status=rejected 的成果
```

请求：部分字段可选（推荐 PATCH）。

```json
{
  "title": "修正后的成果名称",
  "level": "省级"
}
```

编辑规则：
- draft: batch/category/title/achievement_date/level/description/attachment 均可修改
- rejected: category/title/achievement_date/level/description/attachment 可修改，**batch 不可修改**
- submitted/reviewing/counselor_reviewing/approved: 禁止编辑

永久只读字段（不接收客户端传入）：student、class_obj、status、score、submitted_at

------

## **删除成果**

```http
DELETE /achievements/{id}
```

权限：

```text
student     删除自己 status=draft 或 status=rejected 的成果
super_admin 删除任意成果
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

说明：

仅 draft / rejected 状态可删，其余状态禁止删除（见 system-design.md 可删除状态白名单）。

------

# **审核模块**

## **待审核列表**

```http
GET /reviews
```

查询参数：

```text
page          页码
page_size     每页条数
batch_id      批次筛选
```

权限：

```text
evaluator   返回本班待审核成果（status=submitted）
counselor   返回本班待终审成果（status=counselor_reviewing）
审核阶段由当前用户角色自动确定，无需前端传入 stage 参数。
```

------

## **审核通过**

```http
POST /reviews/{id}/approve
```

权限：

```text
当 achievement.status = submitted              → evaluator 可操作
当 achievement.status = counselor_reviewing    → counselor 可操作
```

请求：

```json
{
  "score": 8,
  "comment": "符合认定标准"
}
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 101,
    "status": "counselor_reviewing"
  }
}
```

状态流转：

```text
MVP:
  第一阶段 approve：submitted → counselor_reviewing
  第二阶段 approve：counselor_reviewing → approved
```

------

## **审核退回**

```http
POST /reviews/{id}/return
```

权限：同审核通过。

请求：

```json
{
  "comment": "材料不全，请补充证明"
}
```

状态流转：

```text
MVP:
  第一阶段 return：submitted → draft（退回学生重新编辑）
  第二阶段 return：counselor_reviewing → submitted（退回测评小组重新审核）
```

------

## **审核驳回**

```http
POST /reviews/{id}/reject
```

权限：同审核通过。

请求：

```json
{
  "comment": "不符合认定标准"
}
```

状态流转：

```text
任意阶段 reject：→ rejected（终态）
```

------

# **公示模块**

生成公示

```http
POST /public-notices
```

------

公示列表

```http
GET /public-notices
```

------

结束公示

```http
POST /public-notices/{id}/close
```

------

# **成绩模块**

我的成绩

```http
GET /scores/me
```

------

班级排名

```http
GET /scores/ranking
```

------

# **通知模块**

通知列表

```http
GET /announcements
```

------

发布通知

```http
POST /announcements
```

------

# **导出模块**

## **成绩导出**

```http
GET /export/scores
```

权限：

```text
counselor     导出本班成绩
college_admin 导出本学院成绩
super_admin   导出全部
```

返回：

```text
Excel文件
```

------

# **角色 × 接口权限矩阵**

```text
接口                            | student | evaluator      | counselor      | college_admin | super_admin
-------------------------------|---------|----------------|----------------|---------------|------------
POST /auth/login               | ✓       | ✓              | ✓              | ✓             | ✓
POST /auth/refresh             | ✓       | ✓              | ✓              | ✓             | ✓
GET /auth/profile              | ✓       | ✓              | ✓              | ✓             | ✓
GET /health                    | ✓       | ✓              | ✓              | ✓             | ✓
GET /students/template         | -       | -              | -              | ✓             | ✓
POST /students/import          | -       | -              | -              | ✓             | ✓
GET /batches                   | -       | -              | -              | ✓             | ✓
POST /batches                  | -       | -              | -              | ✓             | ✓
GET /batches/{id}              | -       | -              | -              | ✓             | ✓
PUT /batches/{id}              | -       | -              | -              | ✓             | ✓
DELETE /batches/{id}           | -       | -              | -              | ✓             | ✓
GET /categories                | -       | -              | -              | ✓             | ✓
POST /categories               | -       | -              | -              | ✓             | ✓
GET /categories/{id}           | -       | -              | -              | ✓             | ✓
PUT /categories/{id}           | -       | -              | -              | ✓             | ✓
DELETE /categories/{id}        | -       | -              | -              | ✓             | ✓
GET /achievements              | 自己的  | 本班的         | 本班的         | 本学院的      | 全部
POST /achievements             | ✓       | -              | -              | -             | -
GET /achievements/{id}         | 自己的  | 本班的         | 本班的         | 本学院的      | 全部
PUT /achievements/{id}         | 自己草稿/驳回| -           | -              | -             | -
DELETE /achievements/{id}      | 自己草稿/驳回| -           | -              | -             | -
GET /reviews                   | -       | ✓(第一阶段)    | ✓(第二阶段)    | -             | -
POST /reviews/{id}/approve     | -       | ✓(第一阶段)    | ✓(第二阶段)    | -             | -
POST /reviews/{id}/return      | -       | ✓(第一阶段)    | ✓(第二阶段)    | -             | -
POST /reviews/{id}/reject      | -       | ✓(第一阶段)    | ✓(第二阶段)    | -             | -
POST /public-notices           | -       | -              | ✓              | -             | -
GET /public-notices            | ✓       | ✓              | ✓              | ✓             | ✓
POST /public-notices/{id}/close| -       | -              | ✓              | -             | -
GET /scores/me                 | ✓       | ✓              | -              | -             | -
GET /scores/ranking            | ✓       | ✓              | ✓              | ✓             | ✓
GET /announcements             | ✓       | ✓              | ✓              | ✓             | ✓
POST /announcements            | -       | -              | -              | ✓             | ✓
GET /export/scores             | -       | -              | ✓(本班)        | ✓(本学院)     | ✓
```

说明：

```text
✓            允许
-            禁止
自己的        仅能查看/操作自己的数据
本班的        仅能查看/操作本班的数据
本学院的      仅能查看/操作本学院的数据
(第一阶段)    仅当 achievement.status 为 submitted 时可操作
(第二阶段)    仅当 achievement.status 为 counselor_reviewing 时可操作
```

权限实现：

```text
统一使用 DRF Permission 类控制，禁止在业务代码中 if role == xxx
```

------

END