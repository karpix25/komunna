// Telegram WebApp utilities
import { WebApp } from '@twa-dev/sdk'

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  photo_url?: string
}

export class TelegramWebApp {
  private static instance: TelegramWebApp
  private webApp: typeof WebApp

  private constructor() {
    this.webApp = WebApp
  }

  static getInstance(): TelegramWebApp {
    if (!TelegramWebApp.instance) {
      TelegramWebApp.instance = new TelegramWebApp()
    }
    return TelegramWebApp.instance
  }

  // Проверяем, что приложение запущено в Telegram
  isInTelegram(): boolean {
    return this.webApp.initData !== ''
  }

  // Получаем данные пользователя
  getUser(): TelegramUser | null {
    if (!this.isInTelegram()) {
      return null
    }
    return this.webApp.initDataUnsafe.user || null
  }

  // Инициализация приложения
  init(): void {
    if (this.isInTelegram()) {
      this.webApp.ready()
      this.webApp.expand()
      this.webApp.enableClosingConfirmation()
    }
  }

  // Применяем тему Telegram
  applyTheme(): void {
    if (this.isInTelegram()) {
      const theme = this.webApp.themeParams
      document.documentElement.style.setProperty('--tg-bg-color', theme.bg_color || '#ffffff')
      document.documentElement.style.setProperty('--tg-text-color', theme.text_color || '#000000')
      document.documentElement.style.setProperty('--tg-hint-color', theme.hint_color || '#999999')
      document.documentElement.style.setProperty('--tg-link-color', theme.link_color || '#0088cc')
      document.documentElement.style.setProperty('--tg-button-color', theme.button_color || '#0088cc')
      document.documentElement.style.setProperty('--tg-button-text-color', theme.button_text_color || '#ffffff')
    }
  }

  // Открыть ссылку (Telegram контакт)
  openTelegramLink(username: string): void {
    this.webApp.openTelegramLink(`https://t.me/${username}`)
  }

  // Показать предупреждение
  showAlert(message: string): void {
    this.webApp.showAlert(message)
  }

  // Показать подтверждение
  showConfirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      this.webApp.showConfirm(message, resolve)
    })
  }
}

export const telegram = TelegramWebApp.getInstance()
