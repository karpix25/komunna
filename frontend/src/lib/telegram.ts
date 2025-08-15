// Telegram WebApp utilities with initData validation
declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initData: string;
        initDataUnsafe: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
            language_code?: string;
            is_premium?: boolean;
            photo_url?: string;
          };
          auth_date?: number;
          hash?: string;
        };
        ready: () => void;
        expand: () => void;
        enableClosingConfirmation: () => void;
        themeParams: {
          bg_color?: string;
          text_color?: string;
          hint_color?: string;
          link_color?: string;
          button_color?: string;
          button_text_color?: string;
        };
        openTelegramLink: (url: string) => void;
        showAlert: (message: string) => void;
        showConfirm: (message: string, callback: (confirmed: boolean) => void) => void;
      };
    };
  }
}

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Получаем Telegram WebApp
const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : null;

// Функция для API запросов с авторизацией через initData
async function request(endpoint: string, method: string = "GET", data?: any) {
  if (!tg) {
    throw new Error('Telegram WebApp недоступен');
  }

  const defaultHeaders = {
    'ngrok-skip-browser-warning': 'true',
    'Content-Type': 'application/json',
  };

  const options: RequestInit = {
    method: method,
    headers: {
      Authorization: tg.initData, // Передаем initData для валидации на бэкенде
      'Content-Type': 'application/json',
      ...defaultHeaders,
    },
  };

  // Добавляем body только для методов, которые это поддерживают
  if (method !== 'GET' && method !== 'HEAD' && data) {
    options.body = typeof data === 'string' ? data : JSON.stringify(data);
  }

  const response = await fetch(`${API_URL}/api/${endpoint}`, options);
  const jsonData = await response.json();

  if (!response.ok) {
    console.error('Error details:', jsonData);
    throw new Error(jsonData.message || 'Request failed');
  }

  return jsonData;
}

export class TelegramWebApp {
  private static instance: TelegramWebApp;
  private webApp: typeof tg;

  private constructor() {
    this.webApp = tg;
  }

  static getInstance(): TelegramWebApp {
    if (!TelegramWebApp.instance) {
      TelegramWebApp.instance = new TelegramWebApp();
    }
    return TelegramWebApp.instance;
  }

  // Проверяем наличие initData (значит запущено из Telegram)
  isInTelegram(): boolean {
    return !!(this.webApp && this.webApp.initData);
  }

  // Получаем initData для валидации на бэкенде
  getInitData(): string {
    return this.webApp?.initData || '';
  }

  // Получаем данные пользователя
  getUser(): TelegramUser | null {
    if (!this.isInTelegram()) {
      return null;
    }
    return this.webApp?.initDataUnsafe.user || null;
  }

  // Валидируем пользователя через бэкенд
  async validateUser(): Promise<{ valid: boolean; user?: TelegramUser; error?: string }> {
    try {
      if (!this.isInTelegram()) {
        return { valid: false, error: 'Приложение должно быть запущено из Telegram' };
      }

      // Отправляем initData на бэкенд для валидации
      const response = await request('auth/telegram/validate', 'POST');
      
      return {
        valid: true,
        user: response.user
      };
    } catch (error) {
      return {
        valid: false,
        error: error instanceof Error ? error.message : 'Ошибка валидации'
      };
    }
  }

  // Инициализация приложения
  init(): void {
    if (this.isInTelegram() && this.webApp) {
      this.webApp.ready();
      this.webApp.expand();
      this.webApp.enableClosingConfirmation();
    }
  }

  // Применяем тему Telegram
  applyTheme(): void {
    if (this.isInTelegram() && this.webApp) {
      const theme = this.webApp.themeParams;
      document.documentElement.style.setProperty('--tg-bg-color', theme.bg_color || '#ffffff');
      document.documentElement.style.setProperty('--tg-text-color', theme.text_color || '#000000');
      document.documentElement.style.setProperty('--tg-hint-color', theme.hint_color || '#999999');
      document.documentElement.style.setProperty('--tg-link-color', theme.link_color || '#0088cc');
      document.documentElement.style.setProperty('--tg-button-color', theme.button_color || '#0088cc');
      document.documentElement.style.setProperty('--tg-button-text-color', theme.button_text_color || '#ffffff');
    }
  }

  // Открыть ссылку (Telegram контакт)
  openTelegramLink(username: string): void {
    if (this.webApp) {
      this.webApp.openTelegramLink(`https://t.me/${username}`);
    }
  }

  // Показать предупреждение
  showAlert(message: string): void {
    if (this.webApp) {
      this.webApp.showAlert(message);
    }
  }

  // Показать подтверждение
  showConfirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      if (this.webApp) {
        this.webApp.showConfirm(message, resolve);
      } else {
        resolve(false);
      }
    });
  }
}

export const telegram = TelegramWebApp.getInstance();
export { tg, request };
