# **02-database-design.md**

# **数据库设计文档**

数据库：

MySQL 8.0

字符集：

```sql
utf8mb4
```

排序规则：

```sql
utf8mb4_unicode_ci
```

------

# **一、设计规范**

主键：

```sql
BIGINT AUTO_INCREMENT PRIMARY KEY
```

统一字段：

```sql
created_at DATETIME

updated_at DATETIME
```

------

# **二、核心表**

## **users**

用户表

```text
id

username

password

real_name

student_no

employee_no

phone

email

avatar

status

created_at

updated_at
```

说明：

统一存储：

- 学生
- 辅导员
- 管理员

角色使用：

```text
Django Group
```

管理。

------

## **colleges**

学院表

```text
id

code

name

created_at

updated_at
```

------

## **classes**

班级表

```text
id

college_id

name

grade

counselor_id

created_at

updated_at
```

------

## **evaluation_batches**

测评批次表

字段类型：

```text
字段         | 类型              | 可空 | 默认  | 说明
------------|-------------------|------|-------|------------------------
id          | BIGINT AUTO_INCR  | 否   | -     | 主键
name        | VARCHAR(100)      | 否   | -     | 批次名称
start_time  | DATETIME          | 否   | -     | 开始时间
end_time    | DATETIME          | 否   | -     | 结束时间
status      | TINYINT           | 否   | 0     | 0未开始/1进行中/2已结束
created_at  | DATETIME          | 否   | -     | 创建时间
updated_at  | DATETIME          | 否   | -     | 更新时间
```

状态：

```text
0 未开始

1 进行中

2 已结束
```

------

## **achievement_categories**

成果分类表

```text
id

name

sort_order

created_at

updated_at
```

示例：

```text
学科竞赛

科研成果

社会实践

志愿服务

文体活动
```

------

## **achievements**

成果申报表

字段类型：

```text
字段            | 类型              | 可空 | 默认   | 说明
---------------|-------------------|------|--------|------------------------
id             | BIGINT AUTO_INCR  | 否   | -      | 主键
student_id     | BIGINT            | 否   | -      | FK → users
class_id       | BIGINT            | 否   | -      | FK → classes
batch_id       | BIGINT            | 否   | -      | FK → evaluation_batches
category_id    | BIGINT            | 否   | -      | FK → achievement_categories
title          | VARCHAR(200)      | 否   | -      | 成果名称
level          | VARCHAR(20)       | 是   | NULL   | 成果等级（国家级/省级/校级/院级）
description    | TEXT              | 是   | NULL   | 成果说明
attachment     | VARCHAR(255)      | 是   | NULL   | 附件存储路径
score          | FLOAT             | 是   | NULL   | 认定分数，未审核为空
status         | VARCHAR(20)       | 否   | draft  | choices 枚举
submitted_at   | DATETIME          | 是   | NULL   | 提交时间
created_at     | DATETIME          | 否   | -      | 创建时间
updated_at     | DATETIME          | 否   | -      | 更新时间
```

状态：

```text
draft                草稿

submitted            已提交，待测评小组审核

reviewing            测评小组审核中

counselor_reviewing  测评小组已通过，待辅导员终审

approved             辅导员终审通过（终态）

rejected             已驳回（终态）
```

说明：

状态转换规则见 `system-design.md` 状态转换表。

------

## **audit_records**

审核记录表

字段类型：

```text
字段             | 类型              | 可空 | 默认  | 说明
----------------|-------------------|------|-------|------------------------
id              | BIGINT AUTO_INCR  | 否   | -     | 主键
achievement_id  | BIGINT            | 否   | -     | FK → achievements
reviewer_id     | BIGINT            | 否   | -     | FK → users（审核人）
review_stage    | VARCHAR(20)       | 否   | -     | 审核阶段：evaluator / counselor
action          | VARCHAR(20)       | 否   | -     | choices：approve / reject / return
score           | FLOAT             | 是   | NULL  | 本次认定分数（return 时可为空）
comment         | VARCHAR(500)      | 是   | NULL  | 审核意见
created_at      | DATETIME          | 否   | -     | 审核时间
```

动作：

```text
approve   通过

reject    驳回

return    退回
```

说明：

`review_stage` 区分该条记录属于第一阶段（测评小组）还是第二阶段（辅导员），便于审核轨迹追溯。

------

## **public_notices**

公示表

字段类型：

```text
字段         | 类型              | 可空 | 默认  | 说明
------------|-------------------|------|-------|------------------------
id          | BIGINT AUTO_INCR  | 否   | -     | 主键
batch_id    | BIGINT            | 否   | -     | FK → evaluation_batches
class_id    | BIGINT            | 否   | -     | FK → classes
title       | VARCHAR(200)      | 否   | -     | 公示标题
start_time  | DATETIME          | 否   | -     | 公示开始时间
end_time    | DATETIME          | 否   | -     | 公示结束时间
status      | TINYINT           | 否   | 0     | 0草稿/1公示中/2已结束
created_at  | DATETIME          | 否   | -     | 创建时间
updated_at  | DATETIME          | 否   | -     | 更新时间
```

状态：

```text
0 草稿

1 公示中

2 已结束
```

------

## **score_summaries**

成绩汇总表

字段类型：

```text
字段          | 类型              | 可空 | 默认  | 说明
-------------|-------------------|------|-------|------------------------
id           | BIGINT AUTO_INCR  | 否   | -     | 主键
student_id   | BIGINT            | 否   | -     | FK → users
batch_id     | BIGINT            | 否   | -     | FK → evaluation_batches
total_score  | FLOAT             | 否   | 0     | 该批次总得分
ranking      | INT               | 是   | NULL  | 班级内排名（未汇总时为空）
created_at   | DATETIME          | 否   | -     | 创建时间
updated_at   | DATETIME          | 否   | -     | 更新时间
```

说明：

系统自动计算生成，由统计模块定时/触发汇总。

------

## **announcements**

通知公告表

```text
id

title

content

publisher_id

created_at

updated_at
```

------

## **operation_logs**

操作日志表

```text
id

user_id

module

action

ip

created_at
```

记录：

- 登录
- 新增
- 修改
- 删除
- 审核
- 导出

------

# **三、数据库关系**

```text
College
 │
 └── Class
       │
       ├── Student(User)
       │
       └── Counselor(User)

EvaluationBatch
       │
       └── Achievement
              │
              ├── AchievementCategory
              │
              └── AuditRecord

Achievement
       │
       └── ScoreSummary

PublicNotice

Announcement

OperationLog
```

------

# **四、索引设计**

Achievements：

```sql
student_id

class_id

batch_id

status
```

建立索引。

------

AuditRecords：

```sql
achievement_id

reviewer_id
```

建立索引。

------

ScoreSummaries：

```sql
student_id

batch_id
```

建立联合索引。

------

# **五、MVP暂不设计**

```text
菜单权限表

字典表

消息中心

工作流引擎

附件独立表

评分规则引擎
```

后续版本按需扩展。

END