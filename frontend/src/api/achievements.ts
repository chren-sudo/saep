import apiClient from './client'

export interface AchievementItem {
  id: number
  title: string
  status: string
  status_display: string
  level: string
  score: number | null
  student_name: string
  student_no: string
  category_name: string
  batch_name: string
  achievement_date: string | null
  submitted_at: string | null
  created_at: string
}

export function getAchievements(params?: Record<string, any>) {
  return apiClient.get('/achievements/', { params })
}

export function getAchievement(id: number) {
  return apiClient.get(`/achievements/${id}/`)
}

export function createAchievement(formData: FormData) {
  return apiClient.post('/achievements/', formData)
}

export function updateAchievement(id: number, formData: FormData) {
  return apiClient.put(`/achievements/${id}/`, formData)
}

export function deleteAchievement(id: number) {
  return apiClient.delete(`/achievements/${id}/`)
}

export function submitAchievement(id: number) {
  return apiClient.post(`/achievements/${id}/submit/`)
}

export function canEdit(status: string) {
  return status === 'draft' || status === 'rejected'
}

export function canDelete(status: string) {
  return status === 'draft' || status === 'rejected'
}

export function canSubmit(status: string) {
  return status === 'draft'
}

export function getBatches(params?: any) {
  return apiClient.get('/batches/', { params })
}

export function getCategories() {
  return apiClient.get('/categories/')
}

export const ALLOWED_EXTS = ['.jpg', '.jpeg', '.png', '.pdf']
export const MAX_FILE_SIZE = 10 * 1024 * 1024
