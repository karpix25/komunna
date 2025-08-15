interface ErrorScreenProps {
  message: string
}

export function ErrorScreen({ message }: ErrorScreenProps) {
  return (
    <div className="min-h-screen tg-bg flex items-center justify-center p-4">
      <div className="text-center max-w-sm">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-lg font-semibold tg-text mb-2">Ошибка</h2>
        <p className="tg-hint text-sm mb-4">{message}</p>
        <p className="tg-hint text-xs">
          Пожалуйста, откройте это приложение из Telegram
        </p>
      </div>
    </div>
  )
}
