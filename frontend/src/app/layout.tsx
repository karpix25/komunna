import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Kommuna - Сервис обучения',
  description: 'Создавай курсы и увеличивай активность в сообществе',
}

// ИСПРАВЛЕНО: Выносим viewport в отдельный экспорт
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <head>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
      </head>
      <body>{children}</body>
    </html>
  )
}
