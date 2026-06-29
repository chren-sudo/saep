<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getPublicNotices, createPublicNotice, publishNotice, closeNotice } from '@/api/publicNotices'
import { getBatches } from '@/api/achievements'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const auth = useAuthStore()
const isCounselor = auth.isCounselor

interface NoticeItem {
  id: number; title: string; batch: number; batch_name: string
  class_obj: number; class_name: string
  status: number; status_display: string; approved_count: number
  start_time: string; end_time: string; created_at: string
}

const list = ref<NoticeItem[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const actionLoading = ref<number | null>(null)

// Drawer
const drawerVisible = ref(false)
const formLoading = ref(false)
const batchList = ref<any[]>([])
const form = ref({ batch: null as number | null, class_id: null as number | null, title: '', start_time: '', end_time: '' })

async function load() {
  loading.value = true
  try {
    const res = await getPublicNotices({ page: page.value, page_size: pageSize.value })
    list.value = res.data.data.results
    total.value = res.data.data.total
  } finally { loading.value = false }
}

onMounted(() => load())
watch([page, pageSize], () => load())

async function openDrawer() {
  drawerVisible.value = true
  try {
    const res = await getBatches({ status: 1 })
    batchList.value = res.data.data.results
  } catch { batchList.value = [] }
  form.value = { batch: null, class_id: null, title: '', start_time: '', end_time: '' }
}

async function handleCreate() {
  formLoading.value = true
  try {
    await createPublicNotice({ batch: form.value.batch, class_obj: form.value.class_id, title: form.value.title, start_time: form.value.start_time, end_time: form.value.end_time })
    ElMessage.success('公示生成成功')
    drawerVisible.value = false
    await load()
  } catch (err: any) { ElMessage.error(err.response?.data?.message || '生成失败') }
  finally { formLoading.value = false }
}

async function handlePublish(row: NoticeItem) {
  try { await ElMessageBox.confirm('确认发布该公示？发布后学生可查看。', '提示', { type: 'info' }) } catch { return }
  actionLoading.value = row.id
  try { await publishNotice(row.id); ElMessage.success('已发布'); await load() }
  catch (err: any) { ElMessage.error(err.response?.data?.message || '发布失败') }
  finally { actionLoading.value = null }
}

async function handleClose(row: NoticeItem) {
  try { await ElMessageBox.confirm('确认结束公示？结束后不可恢复。', '提示', { type: 'warning' }) } catch { return }
  actionLoading.value = row.id
  try { await closeNotice(row.id); ElMessage.success('已结束'); await load() }
  catch (err: any) { ElMessage.error(err.response?.data?.message || '结束失败') }
  finally { actionLoading.value = null }
}

function statusTag(status: number) {
  const map: Record<number, { text: string; type: string }> = { 0: { text: '草稿', type: 'info' }, 1: { text: '公示中', type: 'warning' }, 2: { text: '已结束', type: 'success' } }
  return map[status] || { text: '未知', type: 'info' }
}
</script>

<template>
  <div>
    <div style="display:flex;align-items:center;margin-bottom:16px;">
      <h2 style="margin:0;">公示管理</h2>
      <el-button v-if="isCounselor" type="primary" @click="openDrawer" style="margin-left:auto;"><el-icon><Plus /></el-icon>生成公示</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
      <el-table-column prop="batch_name" label="批次" width="160" show-overflow-tooltip />
      <el-table-column prop="class_name" label="班级" width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }"><el-tag :type="statusTag(row.status).type" size="small">{{ statusTag(row.status).text }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="approved_count" label="已通过成果" width="100" align="center" />
      <el-table-column label="操作" width="160" fixed="right" v-if="isCounselor">
        <template #default="{ row }">
          <el-button v-if="row.status===0" type="success" size="small" :loading="actionLoading===row.id" @click="handlePublish(row)">发布</el-button>
          <el-button v-if="row.status===1" type="warning" size="small" :loading="actionLoading===row.id" @click="handleClose(row)">结束</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && list.length===0" description="暂无公示" />

    <div style="display:flex;justify-content:center;margin-top:16px;">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" />
    </div>

    <el-drawer v-model="drawerVisible" title="生成公示" size="420px">
      <el-form :model="form" label-width="80px" v-loading="formLoading">
        <el-form-item label="测评批次" required><el-select v-model="form.batch" style="width:100%"><el-option v-for="b in batchList" :key="b.id" :label="b.name" :value="b.id" /></el-select></el-form-item>
        <el-form-item label="班级" required><el-input v-model="form.class_id" placeholder="输入班级ID" /></el-form-item>
        <el-form-item label="标题" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="开始时间"><el-date-picker v-model="form.start_time" type="datetime" style="width:100%" /></el-form-item>
        <el-form-item label="结束时间"><el-date-picker v-model="form.end_time" type="datetime" style="width:100%" /></el-form-item>
        <el-form-item><el-button type="primary" @click="handleCreate" :loading="formLoading">生成</el-button></el-form-item>
      </el-form>
    </el-drawer>
  </div>
</template>
