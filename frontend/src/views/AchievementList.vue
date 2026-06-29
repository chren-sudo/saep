<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  getAchievements,
  deleteAchievement,
  submitAchievement,
  canEdit,
  canDelete,
  canSubmit,
  type AchievementItem,
} from '@/api/achievements'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import apiClient from '@/api/client'
import AchievementStatusTag from '@/components/achievement/AchievementStatusTag.vue'

const router = useRouter()

const list = ref<AchievementItem[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const filterStatus = ref('')
const auditVisible = ref(false)
const auditRecords = ref<any[]>([])

async function showAudit(row: AchievementItem) {
  const res = await apiClient.get(`/achievements/${row.id}/audit-records/`)
  auditRecords.value = res.data.data
  auditVisible.value = true
}

async function load() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await getAchievements(params)
    const data = res.data.data
    list.value = data.results
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
watch([page, pageSize], () => load())
watch(search, () => { page.value = 1; load() })
watch(filterStatus, () => { page.value = 1; load() })

function goCreate() {
  router.push('/achievements/create')
}

function goEdit(id: number) {
  router.push(`/achievements/${id}/edit`)
}

async function handleDelete(row: AchievementItem) {
  try {
    await ElMessageBox.confirm('确定删除该成果吗？', '提示', { type: 'warning' })
  } catch { return }
  await deleteAchievement(row.id)
  ElMessage.success('删除成功')
  await load()
}

async function handleSubmit(row: AchievementItem) {
  try {
    await ElMessageBox.confirm('提交后将不能继续编辑，是否继续？', '提示', { type: 'info' })
  } catch { return }
  await submitAchievement(row.id)
  ElMessage.success('提交成功')
  await load()
}
</script>

<template>
  <div>
    <div style="display: flex; align-items: center; margin-bottom: 16px;">
      <h2 style="margin: 0;">成果管理</h2>
      <el-button type="primary" @click="goCreate" style="margin-left: auto;">新增成果</el-button>
    </div>

    <div style="display: flex; gap: 12px; margin-bottom: 16px;">
      <el-input v-model="search" placeholder="搜索成果名称" style="width: 240px;" clearable />
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 160px;">
        <el-option label="草稿" value="draft" />
        <el-option label="已提交" value="submitted" />
        <el-option label="测评小组审核中" value="reviewing" />
        <el-option label="待辅导员终审" value="counselor_reviewing" />
        <el-option label="已通过" value="approved" />
        <el-option label="已驳回" value="rejected" />
      </el-select>
    </div>

    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="成果名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="level" label="等级" width="80" />
      <el-table-column prop="batch_name" label="批次" width="160" show-overflow-tooltip />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <AchievementStatusTag :status="row.status" :display="row.status_display" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="goEdit(row.id)"
            v-if="canEdit(row.status)">编辑</el-button>
          <el-button type="success" size="small" @click="handleSubmit(row)"
            v-if="canSubmit(row.status)">提交</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)"
            v-if="canDelete(row.status)">删除</el-button>
          <el-button type="warning" size="small" @click="showAudit(row)">查看记录</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="display: flex; justify-content: center; margin-top: 16px;">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
      />
    </div>

    <el-dialog v-model="auditVisible" title="审核记录" width="500px">
      <el-timeline v-if="auditRecords.length">
        <el-timeline-item v-for="r in auditRecords" :key="r.id"
          :timestamp="r.created_at" placement="top">
          <p><strong>{{ r.review_stage_display }}</strong> — {{ r.action_display }}</p>
          <p v-if="r.comment" style="color:#666">{{ r.comment }}</p>
          <p v-if="r.score">分数: {{ r.score }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无审核记录" />
    </el-dialog>
  </div>
</template>
