"""
TASK-019 AuditRecord 单元测试
"""

from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import User
from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AuditRecord,
)
from apps.evaluations.models import EvaluationBatch
from apps.organizations.models import Class, College
from django.utils import timezone


class AuditRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 学院
        cls.college = College.objects.create(code="CS", name="计算机学院")
        # 班级
        cls.class_obj = Class.objects.create(
            college=cls.college, name="计算机1班", grade="2025级"
        )
        # 学生
        cls.student = User.objects.create_user(
            username="test_student", password="test123",
            real_name="测试学生", student_no="TEST001",
            student_class=cls.class_obj,
        )
        # 审核人
        cls.reviewer = User.objects.create_user(
            username="test_evaluator", password="test123",
            real_name="张评审",
        )
        # 批次
        cls.batch = EvaluationBatch.objects.create(
            name="测试批次",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        # 分类
        cls.category = AchievementCategory.objects.create(
            name="学科竞赛", sort_order=1,
        )
        # 成果
        cls.achievement = Achievement.objects.create(
            student=cls.student,
            class_obj=cls.class_obj,
            batch=cls.batch,
            category=cls.category,
            title="测试成果",
            status=Achievement.Status.SUBMITTED,
        )

    # ============================================================
    # Test 1: AuditRecord 创建成功
    # ============================================================
    def test_01_create_audit_record(self):
        record = AuditRecord.objects.create(
            achievement=self.achievement,
            reviewer=self.reviewer,
            reviewer_name=self.reviewer.real_name,
            review_stage=AuditRecord.ReviewStage.EVALUATOR,
            action=AuditRecord.Action.APPROVE,
            score=Decimal("8.50"),
            comment="材料齐全",
        )
        self.assertEqual(record.review_stage, "evaluator")
        self.assertEqual(record.action, "approve")
        self.assertEqual(record.score, Decimal("8.50"))
        self.assertEqual(record.comment, "材料齐全")
        self.assertIsNotNone(record.created_at)

    # ============================================================
    # Test 2: reviewer_name 正常保存
    # ============================================================
    def test_02_reviewer_name_snapshot(self):
        record = AuditRecord.objects.create(
            achievement=self.achievement,
            reviewer=self.reviewer,
            reviewer_name=self.reviewer.real_name,
            review_stage=AuditRecord.ReviewStage.COUNSELOR,
            action=AuditRecord.Action.REJECT,
            comment="不符合认定标准",
        )
        self.assertEqual(record.reviewer_name, "张评审")
        self.assertEqual(record.reviewer.real_name, "张评审")

    # ============================================================
    # Test 3: score 为 DecimalField
    # ============================================================
    def test_03_score_is_decimal(self):
        record = AuditRecord.objects.create(
            achievement=self.achievement,
            reviewer=self.reviewer,
            reviewer_name=self.reviewer.real_name,
            review_stage=AuditRecord.ReviewStage.EVALUATOR,
            action=AuditRecord.Action.APPROVE,
            score=Decimal("9.00"),
        )
        record.refresh_from_db()
        self.assertIsInstance(record.score, Decimal)
        self.assertEqual(record.score, Decimal("9.00"))

        # Verify null score
        record2 = AuditRecord.objects.create(
            achievement=self.achievement,
            reviewer=self.reviewer,
            reviewer_name=self.reviewer.real_name,
            review_stage=AuditRecord.ReviewStage.EVALUATOR,
            action=AuditRecord.Action.RETURN,
        )
        self.assertIsNone(record2.score)

    # ============================================================
    # Test 4: 删除 reviewer 后, reviewer=NULL, reviewer_name 保留
    # ============================================================
    def test_04_reviewer_deleted_keeps_snapshot(self):
        temp_reviewer = User.objects.create_user(
            username="temp_reviewer", password="test123",
            real_name="临时评审员",
        )
        record = AuditRecord.objects.create(
            achievement=self.achievement,
            reviewer=temp_reviewer,
            reviewer_name=temp_reviewer.real_name,
            review_stage=AuditRecord.ReviewStage.EVALUATOR,
            action=AuditRecord.Action.APPROVE,
            score=Decimal("7.00"),
        )

        # 删除审核人
        record_id = record.id
        temp_reviewer.delete()

        # 重新查询
        record = AuditRecord.objects.get(id=record_id)
        self.assertIsNone(record.reviewer)
        self.assertEqual(record.reviewer_name, "临时评审员")

    # ============================================================
    # Test 5: 删除 achievement 后, AuditRecord 被 CASCADE 删除
    # ============================================================
    def test_05_achievement_deleted_cascades_audit_record(self):
        temp_achievement = Achievement.objects.create(
            student=self.student,
            class_obj=self.class_obj,
            batch=self.batch,
            category=self.category,
            title="临时成果",
            status=Achievement.Status.DRAFT,
        )
        record = AuditRecord.objects.create(
            achievement=temp_achievement,
            reviewer=self.reviewer,
            reviewer_name=self.reviewer.real_name,
            review_stage=AuditRecord.ReviewStage.EVALUATOR,
            action=AuditRecord.Action.REJECT,
            comment="测试CASCADE",
        )
        record_id = record.id
        self.assertTrue(AuditRecord.objects.filter(id=record_id).exists())

        # 删除成果
        temp_achievement.delete()

        # 审核记录应被级联删除
        self.assertFalse(AuditRecord.objects.filter(id=record_id).exists())
