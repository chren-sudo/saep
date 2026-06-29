<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import apiClient from '@/api/client'
import { getBatches } from '@/api/achievements'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const showExport = computed(() => auth.isCounselor || auth.isAdmin)

interface RankItem { ranking: number; student_name: string; student_no: string; class_name: string; total_score: string }
const list = ref<RankItem[]>([])
const loading = ref(false)
const batches = ref<any[]>([])
const batchId = ref<number | null>(null)
const classId = ref('')
const page = ref(1)
const pageSize = ref(20)

async function loadBatches() {
  try { const res = await getBatches(); batches.value = res.data.data.results; if (batches.value.length) batchId.value = batches.value[0].id } catch {}
}

async function load() {
  if (!batchId.value) return
  loading.value = true
  try {
    const params: Record<string, any> = { batch: batchId.value, page: page.value, page_size: pageSize.value }
    if (classId.value) params.class_id = classId.value
    const res = await apiClient.get('/scores/ranking/', { params })
    list.value = res.data.data.results
  } finally { loading.value = false }
}

onMounted(() => loadBatches())
watch(batchId, () => { page.value = 1; load() })
watch(classId, () => { page.value = 1; load() })
watch([page, pageSize], () => load())

function rankIcon(r: number) {
  if (r===1) return '🥇'; if (r===2) return '🥈'; if (r===3) return '🥉'; return ''
}
function rankClass(r: number) {
  if (r===1) return 'color:#ffb800;font-weight:bold'
  if (r===2) return 'color:#909399;font-weight:bold'
  if (r===3) return 'color:#cd7f32;font-weight:bold'
  return ''
}
function exportScores() {
  window.open(`/api/v1/export/scores/?batch=${batchId.value}${classId.value?'&class_id='+classId.value:''}`)
}
</script>

<template>
  <div>
    <div style="display:flex;align-items:center;margin-bottom:16px;">
      <h2 style="margin:0;">排行榜</h2>
      <el-button v-if="showExport" type="success" @click="exportScores" style="margin-left:auto;">导出成绩 Excel</el-button>
    </div>

    <div style="display:flex;gap:12px;margin-bottom:16px;">
      <el-select v-model="batchId" style="width:200px"><el-option v-for="b in batches" :key="b.id" :label="b.name" :value="b.id" /></el-select>
      <el-input v-if="auth.isCounselor||auth.isAdmin" v-model="classId" placeholder="班级ID（可选）" style="width:160px" clearable />
    </div>

    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column label="排名" width="80">
        <template #default="{row}"><span :style="rankClass(row.ranking)">{{ rankIcon(row.ranking) }} {{ row.ranking }}</span></template>
      </el-table-column>
      <el-table-column prop="student_no" label="学号" width="120" />
      <el-table-column prop="student_name" label="姓名" width="100" />
      <el-table-column prop="class_name" label="班级" width="160" />
      <el-table-column prop="total_score" label="总分" width="100" />
    </el-table>

    <el-empty v-if="!loading && list.length===0" description="暂无排名数据" />

    <div style="display:flex;justify-content:center;margin-top:16px;">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="pageSize*10" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" />
    </div>
  </div>
</template>
