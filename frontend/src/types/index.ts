// Common TypeScript types and interfaces

export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  is_superuser: boolean
  telegram_id?: number
  created_at: string
  updated_at: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface ApiError {
  success: false
  error: string
  code?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  username: string
  password: string
  confirmPassword: string
}

export interface HealthCheck {
  status: string
  timestamp: string
}
