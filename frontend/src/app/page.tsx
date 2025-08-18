// frontend/src/app/page.tsx
// ОБНОВЛЕННАЯ главная страница с улучшенной отладкой

'use client'

import { useTelegram } from '@/hooks/useTelegram'
import { TelegramButton } from '@/components/ui/TelegramButton'
import { LoadingScreen } from '@/components/LoadingScreen'
import { ErrorScreen } from '@/components/ErrorScreen'

export default function Home() {
  const { 
    user, 
    isInTelegram, 
    isValidated, 
    isLoading, 
    error, 
    platformInfo,
    retryValidation 
  } = useTelegram()

  // Показываем загрузку во время валидации
  if (isLoading) {
    return <LoadingScreen />
  }

  // В режиме разработки показываем отладочную информацию при ошибках
  if (error && process.env.NODE_ENV === 'development') {
    return (
      <div className="min-h-screen tg-bg safe-area p-4">
        <div className="container mx-auto max-w-md">
          {/* Debug панель */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <h2 className="text-red-800 font-semibold mb-2">🔧 Debug Mode</h2>
            <div className="text-sm text-red-700 space-y-1">
              <p><strong>Ошибка:</strong> {error}</p>
              <p><strong>В Telegram:</strong> {isInTelegram ? '✅' : '❌'}</p>
              <p><strong>Валидирован:</strong> {isValidated ? '✅' : '❌'}</p>
              <p><strong>Платформа:</strong> {platformInfo.platform}</p>
              <p><strong>Версия:</strong> {platformInfo.version}</p>
            </div>
            <button 
              onClick={retryValidation}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded text-sm"
            >
              🔄 Повторить валидацию
            </button>
          </div>

          {/* Показываем контент даже с ошибкой в dev режиме */}
          {user && <MainContent user={user} isValidated={isValidated} />}
        </div>
      </div>
    )
  }

  // В продакшене показываем ошибку
  if (error || !isInTelegram) {
    return <ErrorScreen message={error || 'Доступ запрещен'} />
  }

  // Если нет данных пользователя
  if (!user) {
    return <ErrorScreen message="Не удалось получить данные пользователя" />
  }

  return (
    <div className="min-h-screen tg-bg safe-area">
      <div className="container mx-auto px-4 py-8 max-w-md">
        <MainContent user={user} isValidated={isValidated} />
      </div>
    </div>
  )
}

// Компонент основного контента
function MainContent({ user, isValidated }: { user: any, isValidated: boolean }) {
  const userDisplayName = user.username || user.first_name || 'Пользователь'

  return (
    <>
      {/* Header */}
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">🎓</div>
        <h1 className="text-2xl font-bold tg-text mb-2">
          Добро пожаловать!
        </h1>
        {!isValidated && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2 mb-4">
            <p className="text-yellow-800 text-xs">
              ⚠️ Валидация не пройдена (dev режим)
            </p>
          </div>
        )}
      </div>

      {/* Main Card */}
      <div className="tg-card mb-6">
        <div className="text-center">
          <p className="tg-text text-base leading-relaxed mb-6">
            Привет <span className="font-semibold tg-link">
              {user.username ? `@${user.username}` : userDisplayName}
            </span>! 👋
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

      {/* User Info Card - только в dev режиме */}
      {process.env.NODE_ENV === 'development' && (
        <div className="tg-card mb-6">
          <h3 className="font-semibold tg-text mb-3">🔍 Debug информация:</h3>
          <div className="text-sm tg-hint space-y-1">
            <p><strong>ID:</strong> {user.id}</p>
            <p><strong>Username:</strong> {user.username || 'не указан'}</p>
            <p><strong>Имя:</strong> {user.first_name}</p>
            <p><strong>Фамилия:</strong> {user.last_name || 'не указана'}</p>
            <p><strong>Язык:</strong> {user.language_code || 'не указан'}</p>
            <p><strong>Premium:</strong> {user.is_premium ? 'Да' : 'Нет'}</p>
            <p><strong>Валидирован:</strong> {isValidated ? '✅ Да' : '❌ Нет'}</p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center">
        <p className="tg-hint text-xs">
          Powered by Kommuna © 2024
        </p>
        {process.env.NODE_ENV === 'development' && (
          <p className="tg-hint text-xs mt-1">
            🔧 Development Mode
          </p>
        )}
      </div>
    </>
  )
}
