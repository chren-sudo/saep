# **CLAUDE.md**

# **学生成果认定与综合测评管理平台**

项目代号：

SAEP（Student Achievement Evaluation Platform）

------

# **项目简介**

本项目为高校学生成果认定与综合测评管理平台。

主要解决：

- 学生成果申报
- 成果审核
- 成果公示
- 成绩汇总
- 数据导出

等业务场景。

项目采用：

```yaml
前端:
  Vue3
  TypeScript
  Vite
  Element Plus
  Pinia
  Axios

后端:
  Python 3.12
  Django 5.x
  Django REST Framework
  Simple JWT

数据库:
  MySQL 9.5

部署:
  Ubuntu
  Nginx
  Gunicorn

文件存储:
  media/uploads
```

------

# **开发原则**

## **第一原则**

优先保证：

```text
代码简单
代码可读
代码可维护
```

禁止为了炫技引入复杂设计。

------

## **第二原则**

优先采用 Django 官方推荐方案。

禁止：

```text
重复造轮子
过度封装
过度抽象
```

------

## **第三原则**

所有功能必须遵循 MVP 原则。

当前版本不允许开发：

```text
AI分析

微信小程序

消息推送

工作流引擎

第二课堂

数据驾驶舱

微服务
```

------

# **项目目录规范**

后端目录：

```text
backend/

├── apps/
│
├── config/
│
├── media/
│
├── static/
│
├── logs/
│
├── requirements/
│
└── manage.py
```

------

Apps目录：

```text
apps/

├── accounts
│
├── organizations
│
├── evaluations
│
├── achievements
│
├── publicity
│
├── statistics
│
├── notifications
│
└── system
```

------

# **Django开发规范**

## **Model规范**

所有Model必须继承：

```python
BaseModel
```

BaseModel统一包含：

```python
id

created_at

updated_at
```

示例：

```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

ForeignKey 规范：

```text
on_delete 策略：

  CASCADE    父记录删除则级联删除（学生→成果）

  SET_NULL   置空，需 null=True（辅导员→班级）

  PROTECT    禁止删除被引用记录（分类→成果）

related_name 命名：

  小写 + 复数 + 语义一致

  示例：related_name='achievements'
```

详细定义见 docs/django-models-design.md。

------

## **View规范**

统一使用：

```python
ModelViewSet
```

禁止：

```python
APIView
```

除特殊场景外。

------

## **Serializer规范**

所有接口必须使用：

```python
Serializer
```

进行数据校验。

禁止直接处理 request.data。

------

## **Serializer 嵌套规范**

读取（返回数据）：

```text
使用嵌套 Serializer 返回关联对象。

示例：成果详情返回嵌套的 student / category / batch 对象。
```

写入（接收数据）：

```text
仅接收外键 ID（IntegerField / PrimaryKeyRelatedField）。

禁止在写入时用嵌套 Serializer 创建关联对象。

示例：新增成果接收 category_id，不接收 category 对象。
```

读写分离：

```text
列表/详情用读 Serializer（含嵌套）。

新增/编辑用写 Serializer（仅 ID）。

禁止一个 Serializer 兼顾读写。
```

------

## **统一异常处理**

使用 DRF 自定义异常处理器统一返回格式：

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "config.exception_handler.custom_exception_handler",
}
```

统一处理：

```text
认证失败     → 401，code=401

权限不足     → 403，code=403

资源不存在   → 404，code=404

参数校验失败 → 400，code=400，message 含字段错误详情

非法状态操作 → 400，code=400（如删除不可删除状态的成果）

服务器错误   → 500，code=500
```

禁止在 View 中逐个 try/except 返回不同格式。

业务异常使用 DRF 的 APIException 子类抛出。

------

## **权限规范**

统一使用：

```python
DRF Permission
```

控制权限。

禁止在业务代码中大量使用：

```python
if role == xxx
```

进行权限判断。

------

# **用户与权限设计**

系统角色：

```text
student

evaluator

counselor

college_admin

super_admin
```

角色通过：

```python
Django Group
```

实现。

禁止自建角色表。

------

# **组织架构**

组织关系：

```text
学院
 ↓
班级
 ↓
学生
```

说明：

测评小组成员不是独立组织。

属于：

```text
学生 + evaluator角色
```

由辅导员指定。

------

# **成果审核流程**

固定流程：

```text
学生提交

↓

测评小组审核

↓

辅导员审核

↓

公示

↓

归档
```

禁止跳过审核节点。

------

## **成果状态与删除规则**

成果状态枚举（6 个）：

```text
draft                草稿

submitted            已提交，待测评小组审核

reviewing            测评小组审核中（V2.0 审核锁定机制预留，MVP 不经过此状态）

counselor_reviewing  测评小组已通过，待辅导员终审

approved             辅导员终审通过（终态）

rejected             已驳回（终态）
```

状态转换规则详见 docs/system-design.md 状态转换表。

可删除状态白名单：

```text
仅以下状态允许删除成果：

draft       可删（学生自己的草稿）

rejected    可删（已被驳回）

其余状态禁止删除。
```

编辑规则：

```text
仅 draft / rejected 状态可编辑。

其余状态禁止编辑。
```

------

# **数据库规范**

数据库：

```text
MySQL 8.0
```

------

表命名：

```sql
users

classes

achievements
```

统一：

```text
小写
复数
下划线
```

------

字段命名：

```sql
created_at

updated_at
```

统一下划线风格。

------

主键规范：

```sql
BIGINT AUTO_INCREMENT
```

禁止：

```text
UUID
```

当前阶段不使用。

------

软删除规范

当前版本：

```text
不做软删除
```

直接物理删除。

如需保留历史数据：

增加状态字段。

------

# **API规范**

统一前缀：

```text
/api/v1
```

------

REST风格：

```http
GET

POST

PUT

DELETE
```

------

示例：

```http
GET /api/v1/achievements

POST /api/v1/achievements

GET /api/v1/achievements/{id}

PUT /api/v1/achievements/{id}

DELETE /api/v1/achievements/{id}
```

------

返回格式统一：

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
  "message": "error",
  "data": null
}
```

------

# **文件上传规范**

允许：

```text
jpg

jpeg

png

pdf
```

------

禁止：

```text
zip

rar

exe

bat

js
```

------

上传目录：

```text
media/uploads/
```

------

# **日志规范**

记录：

```text
登录

新增

修改

删除

审核

导出
```

统一写入：

```text
operation_logs
```

------

# **Excel导出规范**

统一使用：

```python
OpenPyXL
```

禁止：

```python
xlwt
```

------

# **前端规范**

技术栈：

```text
Vue3

TypeScript

Element Plus

Pinia

Axios
```

------

页面命名：

```text
AchievementList.vue

AchievementForm.vue

ReviewList.vue
```

采用：

```text
PascalCase
```

------

接口调用统一：

```text
src/api/
```

管理。

禁止在页面中直接写 Axios。

------

# **开发顺序**

严格按照以下顺序开发：

```text
1 用户认证

2 RBAC权限

3 学院班级管理

4 测评批次管理

5 成果分类管理

6 成果申报

7 文件上传

8 测评小组审核

9 辅导员审核

10 公示管理

11 成绩统计

12 Excel导出

13 操作日志
```

禁止跳跃开发。

------

# **Definition Of Done**

功能完成必须满足：

□ 数据库迁移完成

□ Model完成

□ Serializer完成

□ API完成

□ 权限校验完成

□ 操作日志完成

□ 前端页面完成

□ 本地测试通过

□ 无明显Bug

------

# **Claude Code工作要求**

每次开发功能前：

先阅读：

```text
docs/system-design.md

docs/database-design.md

docs/django-models-design.md

docs/api-design.md

docs/development-plan.md
```

开发过程中：

严格遵守：

```text
CLAUDE.md
```

不得擅自修改：

- 技术栈
- 数据库设计
- 权限模型
- 审核流程

除非明确收到新的需求变更。



# **项目状态维护规则**

每完成一个 TASK 后，必须自动执行：

## **更新 current-task.md**

规则：

当前任务完成后：

```text
TASK-001 → TASK-002
TASK-002 → TASK-003
TASK-003 → TASK-004
...
```

自动切换为下一任务。

更新内容：

- Current Task
- Task Name
- Status
- Next Task
- Last Updated

------

## **更新 project-status.md**

更新内容：

### **已完成任务**

新增本次完成任务。

例如：

```text
✓ TASK-001 创建Django项目
✓ TASK-002 JWT认证
```

### **当前任务**

更新为下一任务。

### **项目完成率**

计算公式：

```text
已完成TASK数 / 总TASK数 × 100%
```

### **最近开发记录**

记录：

- 完成了什么
- 修改了哪些模块
- 是否通过验收

------

## **输出要求**

任务结束时必须输出：

1. 本次完成内容
2. 修改文件列表
3. 更新后的 current-task.md
4. 更新后的 project-status.md
5. 下一步建议

然后停止开发，等待人工验收。

未经人工确认，不得自动开始下一任务。







END
------

# **文档同步规则（长期）**

每个 TASK 完成并验收通过后，必须检查并同步更新以下文件：

```text
README.md           ← 技术栈版本、启动命令、已完成 API 列表
current-task.md     ← 当前任务、阶段、下一任务
project-status.md   ← 进度、完成率、已完成/当前/下一阶段
docs/api-design.md  ← 新增接口文档、返回格式、权限矩阵
```

检查原则：

- 如果文档与实际代码状态不一致，优先修正文档
- 新增 API 必须同步到 api-design.md（含权限矩阵）
- 新增数据表必须同步到 README.md（或 database-design.md）
- 进度和完成率必须与已完成 TASK 数一致

END
