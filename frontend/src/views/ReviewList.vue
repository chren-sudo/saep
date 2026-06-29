<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getReviews, approveReview, returnReview, rejectReview } from '@/api/reviews'
import { getAchievement } from '@/api/achievements'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import AchievementStatusTag from '@/components/achievement/AchievementStatusTag.vue'

const auth = useAuthStore()

interface ReviewItem {
  id: number; title: string; student_name: string; student_no: string
  category_name: string; level: string; has_attachment: boolean
  status: string; status_display: string; achievement_date: string | null
  submitted_at: string | null; created_at: string
}

const list = ref<ReviewItem[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')

// Drawer
const drawerVisible = ref(false)
const detail = ref<any>(null)
const detailLoading = ref(false)
const actionLoading = ref('')
const score = ref(0)
const comment = ref('')
const auditRecords = ref<any[]>([])

const isEvaluator = auth.isEvaluator
const isCounselor = auth.isCounselor

async function load() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    const res = await getReviews(params)
    const d = res.data.data
    list.value = d.results
    total.value = d.total
  } finally { loading.value = false }
}

onMounted(() => load())
watch([page, pageSize], () => load())
watch(search, () => { page.value = 1; load() })

async function openDrawer(row: ReviewItem) {
  drawerVisible.value = true
  detailLoading.value = true
  score.value = 0
  comment.value = ''
  try {
    const [res, auditRes] = await Promise.all([
      getAchievement(row.id),
      apiClient.get(`/achievements/${row.id}/audit-records/`),
    ])
    detail.value = res.data.data
    auditRecords.value = auditRes.data.data
  } finally { detailLoading.value = false }
}

function isImage(url: string) {
  return /\.(jpg|jpeg|png)$/i.test(url)
}

async function doAction(action: string) {
  const id = detail.value.id
  const confirmMap: Record<string, { msg: string; type: any }> = {
    approve: { msg: '确认通过该成果？', type: 'info' },
    return: { msg: '确认退回该成果？', type: 'warning' },
    reject: { msg: '确认驳回该成果？', type: 'warning' },
  }
  try {
    await ElMessageBox.confirm(confirmMap[action].msg, '提示', { type: confirmMap[action].type })
  } catch { return }

  actionLoading.value = action
  try {
    if (action === 'approve') await approveReview(id, score.value, comment.value)
    else if (action === 'return') await returnReview(id, comment.value)
    else await rejectReview(id, comment.value)
    ElMessage.success({ approve: '审核通过', return: '已退回', reject: '已驳回' }[action]!)
    drawerVisible.value = false
    await load()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  }
  actionLoading.value = ''
}
</script>

<template>
  <div>
    <h2>成果审核</h2>
    <div style="display: flex; gap: 12px; margin: 16px 0;">
      <el-input v-model="search" placeholder="搜索" style="width: 240px" clearable />
    </div>

    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="title" label="成果名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="student_name" label="学生" width="80" />
      <el-table-column prop="student_no" label="学号" width="120" />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="level" label="等级" width="80" />
      <el-table-column label="附件" width="80">
        <template #default="{ row }">
          <span v-if="row.has_attachment" style="color: #67c23a">有</span>
          <span v-else style="color: #ccc">无</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <AchievementStatusTag :status="row.status" :display="row.status_display" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openDrawer(row)">审核</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="display: flex; justify-content: center; margin-top: 16px;">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
        :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" />
    </div>

    <!-- Drawer -->
    <el-drawer v-model="drawerVisible" title="审核详情" size="480px" direction="rtl">
      <template v-if="detailLoading"><el-skeleton :rows="8" /></template>
      <template v-else-if="detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="成果名称">{{ detail.title }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ detail.category_name }}</el-descriptions-item>
          <el-descriptions-item label="等级">{{ detail.level || '-' }}</el-descriptions-item>
          <el-descriptions-item label="学生">{{ detail.student_name }} ({{ detail.student_no }})</el-descriptions-item>
          <el-descriptions-item label="获得日期">{{ detail.achievement_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="说明">{{ detail.description || '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 附件 -->
        <div v-if="detail.attachment_url" style="margin-top: 16px;">
          <h4>证明材料</h4>
          <template v-if="isImage(detail.attachment_url)">
            <el-image :src="detail.attachment_url" style="max-width:100%;max-height:300px" preview-teleported />
          </template>
          <template v-else>
            <el-link :href="detail.attachment_url" target="_blank" type="primary">📄 打开 PDF</el-link>
          </template>
          <div style="margin-top: 4px;">
            <el-link :href="detail.attachment_url" target="_blank" type="info" :underline="false">下载附件</el-link>
          </div>
        </div>

        <!-- 审核记录 -->
        <div v-if="auditRecords.length" style="margin-top:16px;border-top:1px solid #eee;padding-top:12px;">
          <h4>审核记录</h4>
          <el-timeline>
            <el-timeline-item v-for="r in auditRecords" :key="r.id" :timestamp="r.created_at">
              <strong>{{ r.review_stage_display }}</strong> — {{ r.action_display }}
              <p v-if="r.comment" style="color:#666;margin:0">{{ r.comment }}</p>
              <span v-if="r.score">分数: {{ r.score }}</span>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 审核操作 -->
        <div style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 16px;">
          <!-- approve score -->
          <div style="margin-bottom: 12px;">
            <label style="display:block;margin-bottom:4px;font-weight:bold;">分数（通过时必填）</label>
            <el-input-number v-model="score" :min="0" :max="100" :step="0.5" :precision="1" style="width:100%" />
          </div>
          <!-- comment -->
          <div style="margin-bottom: 12px;">
            <label style="display:block;margin-bottom:4px;font-weight:bold;">审核意见（退回/驳回时必填）</label>
            <el-input v-model="comment" type="textarea" :rows="2" placeholder="请填写审核意见" />
          </div>
          <!-- buttons -->
          <div style="display:flex;gap:8px;">
            <el-button type="success" :loading="actionLoading==='approve'" @click="doAction('approve')">通过</el-button>
            <el-button type="warning" :loading="actionLoading==='return'" @click="doAction('return')">退回</el-button>
            <el-button type="danger" :loading="actionLoading==='reject'" @click="doAction('reject')">驳回</el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>
