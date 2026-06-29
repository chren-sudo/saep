import apiClient from './client'

export function getBatches(params?: any) {
  return apiClient.get('/batches/', { params })
}

export function getReviews() {
  return apiClient.get('/reviews/')
}

export function getAchievements(params?: any) {
  return apiClient.get('/achievements/', { params })
}
