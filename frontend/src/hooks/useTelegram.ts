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
  isLoading: boolean
  error: string | null
}

export function useTelegram(): UseTelegramReturn {
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [isInTelegram, setIsInTelegram] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    try {
      // Инициализируем Telegram WebApp
      telegram.init()
      
      // Проверяем, что мы в Telegram
      const inTelegram = telegram.isInTelegram()
      setIsInTelegram(inTelegram)

      if (inTelegram) {
        // Получаем данные пользователя
        const telegramUser = telegram.getUser()
        setUser(telegramUser)
        
        // Применяем тему Telegram
        telegram.applyTheme()
      } else {
        setError('Приложение должно быть запущено из Telegram')
      }
    } catch (err) {
      setError('Ошибка инициализации Telegram WebApp')
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    user,
    isInTelegram,
    isLoading,
    error
  }
}
