<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import StatisticCard from '@/components/dashboard/StatisticCard.vue'

const auth = useAuthStore()
const dashboard = useDashboardStore()

onMounted(() => dashboard.load())
</script>

<template>
  <div>
    <h1>欢迎, {{ auth.user?.real_name || auth.user?.username }}</h1>
    <p style="color: #909399; margin-bottom: 24px">
      当前批次：{{ dashboard.batchName }}
    </p>

    <el-row :gutter="20" v-loading="dashboard.loading">
      <el-col :span="6" v-if="auth.isEvaluator || auth.isCounselor">
        <StatisticCard title="待审核" :value="dashboard.pendingReviews" color="#e6a23c" />
      </el-col>
      <el-col :span="6" v-if="!auth.isStudent">
        <StatisticCard title="成果总数" :value="dashboard.totalAchievements" />
      </el-col>
      <el-col :span="6" v-if="auth.isAdmin">
        <StatisticCard title="已通过" :value="dashboard.approvedCount" color="#67c23a" />
      </el-col>
      <el-col :span="6" v-if="auth.isStudent">
        <StatisticCard title="我的成果" :value="dashboard.totalAchievements" />
      </el-col>
      <!-- TODO: 后续可增加 Dashboard Summary API，当前继续复用现有接口 -->
    </el-row>
  </div>
</template>
