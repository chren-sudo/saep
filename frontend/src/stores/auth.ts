import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getProfile } from '@/api/auth'

export interface UserInfo {
  id: number
  username: string
  real_name: string
  roles: string[]
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref(localStorage.getItem('access_token') || '')

  const isAuthenticated = computed(() => !!token.value)
  const isStudent = computed(() => user.value?.roles?.includes('student') ?? false)
  const isEvaluator = computed(() => user.value?.roles?.includes('evaluator') ?? false)
  const isCounselor = computed(() => user.value?.roles?.includes('counselor') ?? false)
  const isAdmin = computed(() =>
    ['college_admin', 'super_admin'].some((r) => user.value?.roles?.includes(r)),
  )

  async function loginAction(username: string, password: string) {
    const res = await loginApi(username, password)
    const { access, refresh } = res.data.data
    token.value = access
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    const profileRes = await getProfile()
    user.value = profileRes.data.data
  }

  async function restoreUser() {
    const saved = localStorage.getItem('access_token')
    if (!saved) return
    token.value = saved
    try {
      const profileRes = await getProfile()
      user.value = profileRes.data.data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, token, isAuthenticated, isStudent, isEvaluator, isCounselor, isAdmin, loginAction, logout, restoreUser }
})
