# **system-design.md**

# **学生成果认定与综合测评管理平台**

Student Achievement Evaluation Platform（SAEP）

版本：V1.0

------

# **一、项目概述**

## **项目背景**

高校每年都会开展：

- 综合测评
- 奖学金评定
- 优秀学生评选
- 荣誉称号认定

学生需要提交大量成果材料。

目前大多数院校仍采用：

- Excel统计
- QQ/微信收集材料
- 人工审核
- 手工计算分数

存在以下问题：

- 材料收集困难
- 审核流程不透明
- 数据统计工作量大
- 历史数据难以追溯
- 公示工作繁琐

因此建设统一的学生成果认定与综合测评管理平台。

------

# **二、建设目标**

实现学生成果全流程线上管理：

```text
成果申报

↓

成果审核

↓

成绩认定

↓

公示发布

↓

成绩汇总

↓

数据归档
```

实现：

- 数据统一管理
- 审核流程规范化
- 测评过程透明化
- 成绩统计自动化

------

# **三、系统角色**

## **学生（Student）**

主要职责：

- 提交成果材料
- 修改成果材料
- 查看审核结果
- 查看个人成绩

------

## **测评小组成员（Evaluator）**

说明：

由辅导员从本班学生中指定。

主要职责：

- 审核成果材料
- 填写审核意见
- 认定成果分数

------

## **辅导员（Counselor）**

主要职责：

- 管理本班学生
- 配置测评小组成员
- 终审成果
- 发布公示
- 导出测评结果

------

## **院系管理员（College Admin）**

主要职责：

- 管理班级信息
- 管理测评批次
- 查看学院统计数据

------

## **系统管理员（Super Admin）**

主要职责：

- 用户管理
- 权限管理
- 学院管理
- 系统维护

------

# **四、业务流程设计**

## **整体流程**

```text
学生提交成果

↓

测评小组审核

↓

辅导员审核

↓

审核通过

↓

公示

↓

成绩汇总

↓

归档
```

------

## **成果申报流程**

```text
填写成果信息

↓

上传证明材料

↓

保存草稿

↓

提交审核
```

------

## **审核流程**

两阶段审核，不可跳过任一节点。

### **第一阶段：测评小组审核**

操作人：

```text
evaluator
```

职责：

- 查看成果
- 核验材料
- 填写分数
- 填写审核意见

结果：

```text
通过 / 退回 / 驳回
```

### **第二阶段：辅导员审核**

操作人：

```text
counselor
```

职责：

- 查看测评小组审核结果
- 复核成果
- 确认最终成绩

结果：

```text
通过 / 退回 / 驳回
```

------

### **成果状态枚举**

```text
draft                草稿

submitted            已提交，待测评小组审核

reviewing            测评小组审核中

counselor_reviewing  测评小组已通过，待辅导员终审

approved             辅导员终审通过（终态，进入公示）

rejected             已驳回（终态）
```

说明：

为区分两阶段审核进度，在原 5 状态基础上新增 `counselor_reviewing`。

否则 `reviewing` 同时表示"测评小组审核中"和"待辅导员审核"，会产生歧义。

------

### **状态转换表**

> **MVP V1.0 简化版**：`reviewing` 状态不经过。
> evaluator approve 从 submitted 直接到 counselor_reviewing（一步到位）。
> counselor return 从 counselor_reviewing 回到 submitted（evaluator 重新审核）。
> `reviewing` 状态保留在枚举中，作为 V2.0 审核锁定机制预留。

```text
当前状态              | 动作       | 操作人      | 目标状态             | 说明
---------------------|-----------|-------------|---------------------|------------------------
draft                | submit    | student     | submitted           | 学生提交审核
submitted            | approve   | evaluator   | counselor_reviewing | MVP: evaluator 通过（一步到位）
submitted            | return    | evaluator   | draft               | MVP: 退回学生重新编辑
submitted            | reject    | evaluator   | rejected            | MVP: 测评小组驳回（终态）
counselor_reviewing  | approve   | counselor   | approved            | 辅导员终审通过（终态）
counselor_reviewing  | return    | counselor   | submitted           | MVP: 退回测评小组重新审核
counselor_reviewing  | reject    | counselor   | rejected            | 辅导员驳回（终态）
```

V2.0 完整版（审核锁定后）：

```text
submitted            | approve   | evaluator   | reviewing           | V2.0: 锁定成果，开始审核
reviewing            | approve   | evaluator   | counselor_reviewing | V2.0: 审核通过，转辅导员
reviewing            | return    | evaluator   | draft               | V2.0: 退回学生
reviewing            | reject    | evaluator   | rejected            | V2.0: 驳回
counselor_reviewing  | return    | counselor   | reviewing           | V2.0: 退回测评小组
```

注意：

`return` 含义随阶段不同：

```text
MVP:
  第一阶段 return → 退回给学生（draft），学生可修改后重新提交
  第二阶段 return → 退回给测评小组（submitted），测评小组重新审核

V2.0:
  第二阶段 return → 退回给测评小组（reviewing），测评小组重新审核
```

------

### **可删除状态白名单**

删除成果（DELETE /achievements/{id}）仅允许以下状态：

```text
draft       可删（学生自己的草稿）

rejected    可删（已被驳回，无保留价值）
```

其余状态禁止删除：

```text
submitted            已进入流程，不可删

reviewing            审核中，不可删

counselor_reviewing  待终审，不可删

approved             已认定，不可删（需保留成绩依据）
```

------

## **公示流程**

```text
生成公示名单

↓

发布公示

↓

公示结束

↓

归档
```

------

# **五、系统功能模块**

## **1. 用户与权限模块**

功能：

- 用户登录
- 用户管理
- 角色管理
- 权限控制

角色：

```text
student

evaluator

counselor

college_admin

super_admin
```

------

## **2. 组织架构模块**

功能：

- 学院管理
- 班级管理
- 学生管理

组织结构：

```text
学院
 └── 班级
      └── 学生
```

------

## **3. 测评批次模块**

功能：

- 创建测评批次
- 启用测评批次
- 关闭测评批次

示例：

```text
2026年度综合测评

2026年度奖学金评定
```

------

## **4. 成果分类模块**

功能：

- 分类管理
- 分类排序

示例：

```text
学科竞赛

科研成果

社会实践

志愿服务

文体活动
```

------

## **5. 成果申报模块**

功能：

- 新增成果
- 编辑成果
- 删除成果
- 上传附件
- 查看审核状态

成果信息包括：

```text
成果名称

成果类别

成果等级

成果说明

证明材料
```

------

## **6. 审核管理模块**

功能：

- 待审核列表
- 审核记录
- 审核评分
- 审核意见

审核结果：

```text
通过

退回

驳回
```

------

## **7. 公示管理模块**

功能：

- 生成公示
- 发布公示
- 结束公示

------

## **8. 成绩统计模块**

功能：

- 成绩汇总
- 成绩排名
- 班级统计
- 学院统计

系统自动汇总：

```text
学生总分

班级排名
```

------

## **9. 通知公告模块**

功能：

- 发布通知
- 查看通知

通知类型：

```text
测评通知

公示通知

补交通知
```

------

## **10. 数据导出模块**

功能：

- 成绩导出
- 成果导出

格式：

```text
Excel
```

------

## **11. 操作日志模块**

记录：

```text
登录

新增

修改

删除

审核

导出
```

用于问题追溯与审计。

------

# **六、技术架构**

## **前端**

```text
Vue3
TypeScript
Vite
Element Plus
Pinia
Axios
```

------

## **后端**

```text
Python 3.12

Django 5.x

Django REST Framework

Simple JWT
```

------

## **数据库**

```text
MySQL 8.0
```

------

## **文件存储**

```text
本地文件存储
```

------

# **七、系统设计原则**

## **简单优先**

优先满足业务需求。

避免过度设计。

------

## **MVP优先**

优先实现：

- 申报
- 审核
- 公示
- 统计

核心流程。

------

## **可扩展设计**

后续可扩展：

- 第二课堂
- 自动评分规则
- 微信小程序
- 数据大屏
- AI辅助审核

但不纳入V1.0开发范围。

------

# **八、V1.0范围**

包含：

```text
用户管理

学院班级管理

测评批次管理

成果分类管理

成果申报

成果审核

公示管理

成绩统计

通知公告

Excel导出

操作日志
```

不包含：

```text
AI分析

消息推送

工作流引擎

自动评分规则

移动端
```

END