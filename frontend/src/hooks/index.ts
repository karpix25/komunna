// Custom React Hooks

import { useState, useEffect } from 'react'
import { getFromStorage, setToStorage, removeFromStorage } from '@/utils'

// Local storage hook
export function useLocalStorage<T>(
  key: string, 
  initialValue: T
): [T, (value: T) => void, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = getFromStorage(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  })

  const setValue = (value: T) => {
    try {
      setStoredValue(value)
      setToStorage(key, JSON.stringify(value))
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  const removeValue = () => {
    try {
      setStoredValue(initialValue)
      removeFromStorage(key)
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue, removeValue]
}

// API loading state hook
export function useApiState() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const execute = async <T>(apiCall: () => Promise<T>): Promise<T | null> => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiCall()
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred'
      setError(message)
      return null
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, execute, setError }
}

// Mount state hook
export function useMounted() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return mounted
}
