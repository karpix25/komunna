export function ValidationScreen() {
  return (
    <div className="min-h-screen tg-bg flex items-center justify-center p-4">
      <div className="text-center">
        <div className="text-6xl mb-4">🔐</div>
        <h2 className="text-lg font-semibold tg-text mb-2">Проверка доступа</h2>
        <p className="tg-hint text-sm mb-4">
          Проверяем что вы зашли из Telegram...
        </p>
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 mx-auto" 
             style={{ borderColor: 'var(--tg-button-color)' }}>
        </div>
      </div>
    </div>
  )
}
