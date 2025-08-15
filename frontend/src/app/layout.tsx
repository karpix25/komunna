import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Kommuna - Сервис обучения',
  description: 'Создавай курсы и увеличивай активность в сообществе',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no',
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
