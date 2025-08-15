export function LoadingScreen() {
  return (
    <div className="min-h-screen tg-bg flex items-center justify-center p-4">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-4" 
             style={{ borderColor: 'var(--tg-button-color)' }}>
        </div>
        <p className="tg-hint text-sm">Загрузка...</p>
      </div>
    </div>
  )
}
