<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  value: number | string
  color?: string
}>()

const valueColor = computed(() => props.color || '#409eff')
</script>

<template>
  <el-card shadow="hover">
    <div style="text-align: center">
      <div :style="{ fontSize: '28px', fontWeight: 'bold', color: valueColor }">
        {{ value }}
      </div>
      <div style="margin-top: 8px; color: #909399">{{ title }}</div>
    </div>
  </el-card>
</template>
