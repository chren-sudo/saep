# **django-models-design.md**

# **Django Model 设计文档**

技术栈：

- Django 5.x
- Django REST Framework
- MySQL 8.0

------

# **Apps 划分**

```text
apps/

├── accounts
├── organizations
├── evaluations
├── achievements
├── publicity
├── statistics
├── notifications
└── system
```

------

# **Model 通用规范**

## **继承**

业务模型统一继承 BaseModel：

```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

例外：

OperationLog 只增不改，仅含 created_at，不继承 BaseModel。

## **on_delete 策略**

```text
CASCADE     父记录删除则级联删除（学生→成果、班级→成果）

SET_NULL    父记录删除时置空，需 null=True（辅导员→班级、发布人→通知）

PROTECT     禁止删除被引用的父记录（成果分类→成果）
```

## **related_name 命名**

统一规则：

```text
小写 + 复数 + 与反向查询语义一致
```

示例：

```python
student = ForeignKey(..., related_name='achievements')      # user.achievements
category = ForeignKey(..., related_name='achievements')     # category.achievements
counselor = ForeignKey(..., related_name='managed_classes') # user.managed_classes
```

## **choices 定义**

所有枚举字段统一使用 TextChoices / IntegerChoices：

```python
class Status(models.TextChoices):
    DRAFT = 'draft', '草稿'
```

禁止裸字符串赋值。

------

# **accounts**

## **User**

继承 AbstractUser

新增字段：

```python
real_name = models.CharField(max_length=50)

student_no = models.CharField(max_length=30, blank=True)

employee_no = models.CharField(max_length=30, blank=True)

phone = models.CharField(max_length=20, blank=True)

avatar = models.ImageField(blank=True)

status = models.BooleanField(default=True)
```

说明：

统一管理：

- 学生
- 辅导员
- 院系管理员

角色使用：

```python
Group
Permission
```

实现。

------

# **organizations**

## **College**

```python
class College(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
```

------

## **Class**

```python
class Class(BaseModel):
    college = models.ForeignKey(
        College, on_delete=models.CASCADE, related_name='classes'
    )
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    counselor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_classes'
    )
```

关联：

```python
college   -> College  (CASCADE，学院删除则班级级联删除)

counselor -> User     (SET_NULL，辅导员离职不影响班级存在)
```

------

# **evaluations**

## **EvaluationBatch**

```python
class EvaluationBatch(BaseModel):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, '未开始'
        RUNNING = 1, '进行中'
        FINISHED = 2, '已结束'

    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.IntegerField(
        choices=Status.choices, default=Status.NOT_STARTED
    )
```

状态：

```python
NOT_STARTED  未开始

RUNNING      进行中

FINISHED     已结束
```

------

# **achievements**

## **AchievementCategory**

```python
class AchievementCategory(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    sort_order = models.IntegerField(default=0)
```

------

## **Achievement**

```python
class Achievement(BaseModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        SUBMITTED = 'submitted', '已提交'
        REVIEWING = 'reviewing', '测评小组审核中'
        COUNSELOR_REVIEWING = 'counselor_reviewing', '待辅导员终审'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已驳回'

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='achievements'
    )
    class_obj = models.ForeignKey(
        'organizations.Class', on_delete=models.CASCADE,
        related_name='achievements'
    )
    batch = models.ForeignKey(
        'evaluations.EvaluationBatch', on_delete=models.CASCADE,
        related_name='achievements'
    )
    category = models.ForeignKey(
        AchievementCategory, on_delete=models.PROTECT,
        related_name='achievements'
    )
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    attachment = models.FileField(upload_to='uploads/%Y/%m/', blank=True)
    score = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
```

状态：

```python
DRAFT                草稿

SUBMITTED            已提交，待测评小组审核

REVIEWING            测评小组审核中

COUNSELOR_REVIEWING  测评小组已通过，待辅导员终审

APPROVED             辅导员终审通过（终态）

REJECTED             已驳回（终态）
```

------

## **AuditRecord**

```python
class AuditRecord(BaseModel):
    class ReviewStage(models.TextChoices):
        EVALUATOR = 'evaluator', '测评小组'
        COUNSELOR = 'counselor', '辅导员'

    class Action(models.TextChoices):
        APPROVE = 'approve', '通过'
        REJECT = 'reject', '驳回'
        RETURN = 'return', '退回'

    achievement = models.ForeignKey(
        Achievement, on_delete=models.CASCADE,
        related_name='audit_records'
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='audit_records'
    )
    review_stage = models.CharField(max_length=20, choices=ReviewStage.choices)
    action = models.CharField(max_length=20, choices=Action.choices)
    score = models.FloatField(null=True, blank=True)
    comment = models.CharField(max_length=500, blank=True)
```

动作：

```python
APPROVE   通过

REJECT    驳回

RETURN    退回
```

说明：

`review_stage` 区分审核阶段，与 `system-design.md` 状态转换表对应。

------

# **publicity**

## **PublicNotice**

```python
class PublicNotice(BaseModel):
    class Status(models.IntegerChoices):
        DRAFT = 0, '草稿'
        PUBLISHED = 1, '公示中'
        CLOSED = 2, '已结束'

    batch = models.ForeignKey(
        'evaluations.EvaluationBatch', on_delete=models.CASCADE,
        related_name='public_notices'
    )
    class_obj = models.ForeignKey(
        'organizations.Class', on_delete=models.CASCADE,
        related_name='public_notices'
    )
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.IntegerField(
        choices=Status.choices, default=Status.DRAFT
    )
```

------

# **statistics**

## **ScoreSummary**

```python
class ScoreSummary(BaseModel):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='score_summaries'
    )
    batch = models.ForeignKey(
        'evaluations.EvaluationBatch', on_delete=models.CASCADE,
        related_name='score_summaries'
    )
    total_score = models.FloatField(default=0)
    ranking = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [('student', 'batch')]
        indexes = [
            models.Index(fields=['student', 'batch']),
        ]
```

说明：

通过定时任务生成。

------

# **notifications**

## **Announcement**

```python
class Announcement(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    publisher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='announcements'
    )
```

------

# **system**

## **OperationLog**

```python
class OperationLog(models.Model):
    class Module(models.TextChoices):
        AUTH = 'auth', '认证'
        ACHIEVEMENT = 'achievement', '成果'
        REVIEW = 'review', '审核'
        PUBLICITY = 'publicity', '公示'
        STATISTICS = 'statistics', '统计'
        EXPORT = 'export', '导出'
        SYSTEM = 'system', '系统'

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='operation_logs'
    )
    module = models.CharField(max_length=20, choices=Module.choices)
    action = models.CharField(max_length=50)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

记录：

- 登录
- 提交成果
- 审核
- 删除
- 导出

说明：

OperationLog 不继承 BaseModel，只有 created_at（日志只增不改）。