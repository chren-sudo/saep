import apiClient from './client'

export function getPublicNotices(params?: Record<string, any>) {
  return apiClient.get('/public-notices/', { params })
}

export function createPublicNotice(data: Record<string, any>) {
  return apiClient.post('/public-notices/', data)
}

export function publishNotice(id: number) {
  return apiClient.post(`/public-notices/${id}/publish/`)
}

export function closeNotice(id: number) {
  return apiClient.post(`/public-notices/${id}/close/`)
}
