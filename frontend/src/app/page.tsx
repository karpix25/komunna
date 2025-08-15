'use client'

import { useTelegram } from '@/hooks/useTelegram'
import { TelegramButton } from '@/components/ui/TelegramButton'
import { LoadingScreen } from '@/components/LoadingScreen'
import { ErrorScreen } from '@/components/ErrorScreen'

export default function Home() {
  const { user, isInTelegram, isLoading, error } = useTelegram()

  if (isLoading) {
    return <LoadingScreen />
  }

  if (error || !isInTelegram) {
    return <ErrorScreen message={error || 'Приложение должно быть запущено из Telegram'} />
  }

  if (!user) {
    return <ErrorScreen message="Не удалось получить данные пользователя" />
  }

  const userDisplayName = user.username || user.first_name || 'Пользователь'

  return (
    <div className="min-h-screen tg-bg safe-area">
      <div className="container mx-auto px-4 py-8 max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🎓</div>
          <h1 className="text-2xl font-bold tg-text mb-2">
            Добро пожаловать!
          </h1>
        </div>

        {/* Main Card */}
        <div className="tg-card mb-6">
          <div className="text-center">
            <p className="tg-text text-base leading-relaxed mb-6">
              Привет <span className="font-semibold tg-link">@{userDisplayName}</span>! 👋
              <br /><br />
              Это сервис <span className="font-semibold">Kommuna</span> для обучения.
              <br /><br />
              Если хочешь создавать свои курсы и увеличивать активность в своем сообществе, напиши админу.
            </p>
            
            <TelegramButton 
              username="karlo25"
              variant="primary"
            >
              📱 Написать
            </TelegramButton>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="tg-hint text-xs">
            Powered by Kommuna © 2024
          </p>
        </div>
      </div>
    </div>
  )
}
