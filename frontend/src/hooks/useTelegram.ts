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
          // Для разработки - показываем ошибку, но позволяем продолжить
          if (process.env.NODE_ENV === 'development') {
            console.warn('⚠️ Не в Telegram - используем тестовые данные')
            const mockUser: TelegramUser = {
              id: 123456789,
              first_name: "Test User",
              username: "testuser",
              language_code: "ru"
            }
            setUser(mockUser)
            setIsValidated(true)
            setIsLoading(false)
            return
          } else {
            setError('Приложение должно быть запущено из Telegram')
            setIsLoading(false)
            return
          }
        }

        // Применяем тему Telegram
        telegram.applyTheme()

        // Проверяем наличие initData
        const initData = telegram.getInitData()
        if (!initData) {
          setError('Отсутствуют данные авторизации Telegram')
          setIsLoading(false)
          return
        }

        // Валидируем пользователя через backend
        console.log('🔐 Начинаем валидацию через backend...')
        const validation = await telegram.validateUser()
        
        if (validation.valid && validation.user) {
          console.log('✅ Валидация успешна:', validation.user)
          setUser(validation.user)
          setIsValidated(true)
        } else {
          console.error('❌ Ошибка валидации:', validation.error)
          setError(validation.error || 'Ошибка валидации пользователя')
        }
      } catch (err) {
        console.error('❌ Критическая ошибка:', err)
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
