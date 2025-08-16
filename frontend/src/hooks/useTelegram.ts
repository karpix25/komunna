'use client'

import { useEffect, useState } from 'react'
import { telegram } from '@/lib/telegram'

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  photo_url?: string
}

interface UseTelegramReturn {
  user: TelegramUser | null
  isInTelegram: boolean
  isValidated: boolean
  isLoading: boolean
  error: string | null
}

export function useTelegram(): UseTelegramReturn {
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [isInTelegram, setIsInTelegram] = useState(false)
  const [isValidated, setIsValidated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initializeTelegram = async () => {
      try {
        // Инициализируем Telegram WebApp
        telegram.init()
        
        // Проверяем, что мы в Telegram
        const inTelegram = telegram.isInTelegram()
        setIsInTelegram(inTelegram)

        if (!inTelegram) {
          // Для тестирования - имитируем пользователя
          const mockUser: TelegramUser = {
            id: 123456789,
            first_name: "Test",
            username: "testuser"
          }
          setUser(mockUser)
          setIsValidated(true)
          setIsLoading(false)
          return
        }

        // Применяем тему Telegram
        telegram.applyTheme()

        // Получаем пользователя из Telegram (без валидации backend)
        const telegramUser = telegram.getUser()
        
        if (telegramUser) {
          setUser(telegramUser)
          setIsValidated(true) // Временно считаем валидным
        } else {
          setError('Не удалось получить данные пользователя')
        }
      } catch (err) {
        setError('Ошибка инициализации Telegram WebApp')
      } finally {
        setIsLoading(false)
      }
    }

    initializeTelegram()
  }, [])

  return {
    user,
    isInTelegram,
    isValidated,
    isLoading,
    error
  }
}
