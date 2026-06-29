<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container style="min-height: 100vh">
    <el-aside width="200px" style="background: #304156;">
      <div style="height: 60px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: bold;">
        SAEP
      </div>
      <el-menu :default-active="activeMenu" router background-color="#304156" text-color="#bfcbd9"
        active-text-color="#409eff">
        <el-menu-item index="/">
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/achievements">
          <span>成果管理</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isEvaluator || authStore.isCounselor" index="/reviews">
          <span>成果审核</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isCounselor || authStore.isAdmin" index="/students" disabled>
          <span>学生管理</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isCounselor || authStore.isAdmin" index="/public-notices">
          <span>公示管理</span>
        </el-menu-item>
        <el-menu-item index="/my-scores">
          <span>成绩查询</span>
        </el-menu-item>
        <el-menu-item index="/ranking">
          <span>排行榜</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;align-items:center;background:#fff;border-bottom:1px solid #e6e6e6;">
        <span style="margin-left:auto;cursor:pointer;color:#409eff" @click="handleLogout">
          {{ authStore.user?.real_name }} | 退出
        </span>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
