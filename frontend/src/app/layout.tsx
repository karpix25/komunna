import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Kommuna - Платформа для обучения',
  description: 'Создавайте курсы и развивайте сообщества в Telegram',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}