import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// Utility for merging Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Date formatting
export const formatDate = (date: string | Date, locale = 'ru-RU') => {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

// Email validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Password strength validation
export const isStrongPassword = (password: string): boolean => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/
  return passwordRegex.test(password)
}

// Sleep utility for testing
export const sleep = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms))

// Local storage helpers
export const getFromStorage = (key: string): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(key)
}

export const setToStorage = (key: string, value: string): void => {
  if (typeof window === 'undefined') return
  localStorage.setItem(key, value)
}

export const removeFromStorage = (key: string): void => {
  if (typeof window === 'undefined') return
  localStorage.removeItem(key)
}
