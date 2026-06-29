import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAchievements, getBatches, getReviews } from '@/api/dashboard'
import { useAuthStore } from './auth'

export const useDashboardStore = defineStore('dashboard', () => {
  const totalAchievements = ref(0)
  const pendingReviews = ref(0)
  const approvedCount = ref(0)
  const batchName = ref('')
  const loading = ref(false)

  async function load() {
    const auth = useAuthStore()
    loading.value = true

    // 分别加载，单个失败不影响其他
    try {
      const res = await getBatches({ status: 1 })
      const batches = res.data.data.results
      batchName.value = batches.length > 0 ? batches[0].name : '暂无进行中的批次'
    } catch { batchName.value = '暂无进行中的批次' }

    try {
      if (auth.isEvaluator || auth.isCounselor) {
        const res = await getReviews()
        pendingReviews.value = res.data.data.total
      }
    } catch { pendingReviews.value = 0 }

    try {
      const res = await getAchievements()
      totalAchievements.value = res.data.data.total || 0
    } catch { totalAchievements.value = 0 }

    try {
      if (auth.isAdmin) {
        const res = await getAchievements({ status: 'approved' })
        approvedCount.value = res.data.data.total || 0
      }
    } catch { approvedCount.value = 0 }

    loading.value = false
  }

  return { totalAchievements, pendingReviews, approvedCount, batchName, loading, load }
})
