import apiClient from './client'

export function getReviews(params?: Record<string, any>) {
  return apiClient.get('/reviews/', { params })
}

export function approveReview(id: number, score: number, comment?: string) {
  return apiClient.post(`/reviews/${id}/approve/`, { score, comment: comment || '' })
}

export function returnReview(id: number, comment: string) {
  return apiClient.post(`/reviews/${id}/return/`, { comment })
}

export function rejectReview(id: number, comment: string) {
  return apiClient.post(`/reviews/${id}/reject/`, { comment })
}
