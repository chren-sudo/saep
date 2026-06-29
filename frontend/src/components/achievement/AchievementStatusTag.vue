<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string; display: string }>()

const statusType = computed(() => {
  const map: Record<string, string> = {
    draft: 'info',
    submitted: 'warning',
    reviewing: 'warning',
    counselor_reviewing: '',
    approved: 'success',
    rejected: 'danger',
  }
  return map[props.status] || 'info'
})
</script>

<template>
  <el-tag :type="statusType">{{ display }}</el-tag>
</template>
