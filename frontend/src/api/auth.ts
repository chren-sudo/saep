import apiClient from './client'

export function login(username: string, password: string) {
  return apiClient.post('/auth/login/', { username, password })
}

export function getProfile() {
  return apiClient.get('/auth/profile/')
}
