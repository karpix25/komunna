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
          setError('Приложение должно быть запущено из Telegram')
          setIsLoading(false)
          return
        }

        // Применяем тему Telegram
        telegram.applyTheme()

        // Валидируем пользователя через бэкенд
        const validation = await telegram.validateUser()
        
        if (validation.valid && validation.user) {
          setUser(validation.user)
          setIsValidated(true)
        } else {
          setError(validation.error || 'Ошибка валидации пользователя')
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
