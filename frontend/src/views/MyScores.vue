<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getAchievements, getBatches } from '@/api/achievements'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(false)
const batches = ref<any[]>([])
const batchId = ref<number | null>(null)
const scoreData = ref<{ total_score: string; ranking: number; class_name: string } | null>(null)

async function loadBatches() {
  try { const res = await getBatches(); batches.value = res.data.data.results; if (batches.value.length) batchId.value = batches.value[0].id } catch {}
}

async function loadScores() {
  if (!batchId.value) return
  loading.value = true
  try {
    const res = await apiClient.get('/scores/', { params: { batch: batchId.value } })
    const results = res.data.data.results
    scoreData.value = results.length > 0 ? results[0] : null
  } finally { loading.value = false }
}

onMounted(() => loadBatches())
watch(batchId, () => loadScores())
</script>

<template>
  <div>
    <h2>我的成绩</h2>
    <div style="margin:16px 0;">
      <el-select v-model="batchId" placeholder="选择批次" style="width:240px">
        <el-option v-for="b in batches" :key="b.id" :label="b.name" :value="b.id" />
      </el-select>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-empty v-if="!loading && !scoreData" description="暂无成绩数据" />
      <template v-if="scoreData">
        <el-col :span="8">
          <el-card shadow="hover"><div style="text-align:center">
            <div style="color:#909399;font-size:14px">总分</div>
            <div style="font-size:36px;font-weight:bold;color:#409eff;margin:8px 0">{{ scoreData.total_score }}</div>
          </div></el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover"><div style="text-align:center">
            <div style="color:#909399;font-size:14px">班级排名</div>
            <div style="font-size:36px;font-weight:bold;color:#e6a23c;margin:8px 0">
              <span v-if="scoreData.ranking===1">🥇</span>
              <span v-else-if="scoreData.ranking===2">🥈</span>
              <span v-else-if="scoreData.ranking===3">🥉</span>
              {{ scoreData.ranking || '-' }}
            </div>
          </div></el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover"><div style="text-align:center">
            <div style="color:#909399;font-size:14px">班级</div>
            <div style="font-size:20px;font-weight:bold;color:#333;margin:8px 0">{{ scoreData.class_name }}</div>
          </div></el-card>
        </el-col>
      </template>
    </el-row>
  </div>
</template>
