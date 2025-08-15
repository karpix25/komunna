interface ErrorScreenProps {
  message: string
}

export function ErrorScreen({ message }: ErrorScreenProps) {
  const isAuthError = message.includes('Telegram') || message.includes('валидации')
  
  return (
    <div className="min-h-screen tg-bg flex items-center justify-center p-4">
      <div className="text-center max-w-sm">
        <div className="text-4xl mb-4">
          {isAuthError ? '🔒' : '⚠️'}
        </div>
        <h2 className="text-lg font-semibold tg-text mb-2">
          {isAuthError ? 'Доступ ограничен' : 'Ошибка'}
        </h2>
        <p className="tg-hint text-sm mb-4">{message}</p>
        {isAuthError && (
          <div className="tg-card p-4 text-left">
            <p className="tg-hint text-xs leading-relaxed">
              📱 Откройте это приложение через Telegram Mini Apps
              <br />
              🔗 Или воспользуйтесь прямой ссылкой от бота
              <br />
              🛡️ Доступ разрешен только из Telegram
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
