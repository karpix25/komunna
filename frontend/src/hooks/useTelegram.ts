// frontend/src/hooks/useTelegram.ts
// ИСПРАВЛЕННАЯ версия хука для Telegram WebApp

'use client'

import { useEffect, useState } from 'react'
import { telegram, debugTelegram } from '@/lib/telegram'

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
  platformInfo: { platform: string; version: string; inTelegram: boolean }
  retryValidation: () => void
}

export function useTelegram(): UseTelegramReturn {
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [isInTelegram, setIsInTelegram] = useState(false)
  const [isValidated, setIsValidated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [platformInfo, setPlatformInfo] = useState({ 
    platform: 'unknown', 
    version: 'unknown', 
    inTelegram: false 
  })

  const initializeTelegram = async () => {
    try {
      console.log('🚀 Начинаем инициализацию Telegram WebApp...')
      setIsLoading(true)
      setError(null)

      // Ждем немного для загрузки Telegram WebApp
      await new Promise(resolve => setTimeout(resolve, 100))

      // Отладочная информация
      const debugInfo = debugTelegram()
      console.log('🔍 Debug info:', debugInfo)

      // Инициализируем Telegram WebApp
      telegram.init()
      
      // Получаем информацию о платформе
      const platformInfo = telegram.getPlatformInfo()
      setPlatformInfo(platformInfo)
      console.log('📱 Platform info:', platformInfo)

      // Проверяем, что мы в Telegram
      const inTelegram = telegram.isInTelegram()
      setIsInTelegram(inTelegram)
      console.log('🔍 In Telegram:', inTelegram)

      if (!inTelegram) {
        // Для разработки - разрешаем тестирование вне Telegram
        if (process.env.NODE_ENV === 'development') {
          console.warn('⚠️ DEVELOPMENT MODE: Не в Telegram - используем тестовые данные')
          
          const mockUser: TelegramUser = {
            id: 123456789,
            first_name: "Test User",
            username: "testuser",
            language_code: "ru",
            is_premium: false
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

      // Получаем initData
      const initData = telegram.getInitData()
      console.log('📊 InitData получен:', !!initData, 'длина:', initData.length)

      if (!initData) {
        setError('Отсутствуют данные авторизации Telegram')
        setIsLoading(false)
        return
      }

      // Проверяем данные пользователя из initDataUnsafe
      const telegramUser = telegram.getUser()
      if (!telegramUser) {
        setError('Не удалось получить данные пользователя из Telegram')
        setIsLoading(false)
        return
      }

      console.log('👤 Пользователь Telegram:', telegramUser)

      // Валидируем пользователя через backend
      console.log('🔐 Начинаем валидацию через backend...')
      const validation = await telegram.validateUser()
      console.log('📋 Результат валидации:', validation)
      
      if (validation.valid && validation.user) {
        console.log('✅ Валидация успешна!')
        setUser(validation.user)
        setIsValidated(true)
      } else {
        console.error('❌ Ошибка валидации:', validation.error)
        setError(validation.error || 'Ошибка валидации пользователя')
        
        // В режиме разработки показываем данные пользователя даже при ошибке валидации
        if (process.env.NODE_ENV === 'development') {
          console.warn('⚠️ DEVELOPMENT MODE: Показываем пользователя несмотря на ошибку валидации')
          setUser(telegramUser)
          setIsValidated(false) // Помечаем как невалидированного
        }
      }

    } catch (err) {
      console.error('❌ Критическая ошибка инициализации:', err)
      const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка'
      setError(`Ошибка инициализации: ${errorMessage}`)
      
      // В режиме разработки пытаемся продолжить
      if (process.env.NODE_ENV === 'development') {
        console.warn('⚠️ DEVELOPMENT MODE: Продолжаем несмотря на ошибку')
        const mockUser: TelegramUser = {
          id: 123456789,
          first_name: "Debug User",
          username: "debuguser",
          language_code: "ru"
        }
        setUser(mockUser)
        setIsValidated(false)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const retryValidation = () => {
    console.log('🔄 Повторная попытка валидации...')
    initializeTelegram()
  }

  useEffect(() => {
    // Запускаем инициализацию только в браузере
    if (typeof window !== 'undefined') {
      initializeTelegram()
    }
  }, [])

  return {
    user,
    isInTelegram,
    isValidated,
    isLoading,
    error,
    platformInfo,
    retryValidation
  }
}
