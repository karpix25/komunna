// frontend/src/lib/telegram.ts
// ИСПРАВЛЕННАЯ версия Telegram WebApp utilities

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
            allows_write_to_pm?: boolean;
          };
          auth_date?: number;
          hash?: string;
          query_id?: string;
        };
        ready: () => void;
        expand: () => void;
        enableClosingConfirmation: () => void;
        disableClosingConfirmation: () => void;
        themeParams: {
          bg_color?: string;
          text_color?: string;
          hint_color?: string;
          link_color?: string;
          button_color?: string;
          button_text_color?: string;
          secondary_bg_color?: string;
        };
        openTelegramLink: (url: string) => void;
        showAlert: (message: string) => void;
        showConfirm: (message: string, callback: (confirmed: boolean) => void) => void;
        platform: string;
        version: string;
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

  // ИСПРАВЛЕНО: Проверяем наличие initData
  isInTelegram(): boolean {
    if (!this.webApp) {
      console.warn('⚠️ Telegram WebApp не найден');
      return false;
    }
    
    const hasInitData = !!(this.webApp.initData && this.webApp.initData.length > 0);
    console.log(`🔍 Telegram WebApp проверка:`, {
      webAppExists: !!this.webApp,
      hasInitData,
      initDataLength: this.webApp.initData?.length || 0,
      platform: this.webApp.platform,
      version: this.webApp.version
    });
    
    return hasInitData;
  }

  // ИСПРАВЛЕНО: Получаем initData для валидации
  getInitData(): string {
    if (!this.webApp || !this.webApp.initData) {
      console.warn('⚠️ initData отсутствует');
      return '';
    }
    
    console.log('🔍 initData получен:', {
      length: this.webApp.initData.length,
      preview: this.webApp.initData.substring(0, 100) + '...'
    });
    
    return this.webApp.initData;
  }

  // Получаем данные пользователя
  getUser(): TelegramUser | null {
    if (!this.isInTelegram()) {
      return null;
    }
    
    const user = this.webApp?.initDataUnsafe.user;
    if (!user) {
      console.warn('⚠️ Данные пользователя отсутствуют в initDataUnsafe');
      return null;
    }
    
    console.log('👤 Данные пользователя получены:', {
      id: user.id,
      first_name: user.first_name,
      username: user.username
    });
    
    return user;
  }

  // ИСПРАВЛЕНО: Валидируем пользователя через бэкенд
  async validateUser(): Promise<{ valid: boolean; user?: TelegramUser; error?: string }> {
    try {
      if (!this.isInTelegram()) {
        return { 
          valid: false, 
          error: 'Приложение должно быть запущено из Telegram' 
        };
      }

      const initData = this.getInitData();
      if (!initData) {
        return { 
          valid: false, 
          error: 'Отсутствуют данные авторизации Telegram' 
        };
      }

      console.log('🔐 Отправляем initData на валидацию...');

      // ИСПРАВЛЕНО: Отправляем initData напрямую в заголовке Authorization
      const response = await fetch(`${API_URL}/api/auth/telegram/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': initData, // Отправляем initData как есть
          'ngrok-skip-browser-warning': 'true'
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Ошибка валидации:', response.status, errorText);
        return {
          valid: false,
          error: `Ошибка сервера: ${response.status}`
        };
      }

      const result = await response.json();
      console.log('✅ Результат валидации:', result);

      return result;
      
    } catch (error) {
      console.error('❌ Критическая ошибка валидации:', error);
      return {
        valid: false,
        error: error instanceof Error ? error.message : 'Ошибка валидации'
      };
    }
  }

  // Инициализация приложения
  init(): void {
    if (!this.webApp) {
      console.warn('⚠️ Telegram WebApp недоступен для инициализации');
      return;
    }

    console.log('🚀 Инициализация Telegram WebApp...');
    
    try {
      this.webApp.ready();
      this.webApp.expand();
      this.webApp.enableClosingConfirmation();
      
      console.log('✅ Telegram WebApp инициализирован:', {
        platform: this.webApp.platform,
        version: this.webApp.version,
        theme: this.webApp.themeParams
      });
    } catch (error) {
      console.error('❌ Ошибка инициализации WebApp:', error);
    }
  }

  // ИСПРАВЛЕНО: Применяем тему Telegram
  applyTheme(): void {
    if (!this.webApp) {
      console.warn('⚠️ Telegram WebApp недоступен для применения темы');
      return;
    }

    try {
      const theme = this.webApp.themeParams;
      console.log('🎨 Применяем тему Telegram:', theme);

      const root = document.documentElement;
      
      // Применяем цвета темы с fallback значениями
      root.style.setProperty('--tg-bg-color', theme.bg_color || '#ffffff');
      root.style.setProperty('--tg-text-color', theme.text_color || '#000000');
      root.style.setProperty('--tg-hint-color', theme.hint_color || '#999999');
      root.style.setProperty('--tg-link-color', theme.link_color || '#0088cc');
      root.style.setProperty('--tg-button-color', theme.button_color || '#0088cc');
      root.style.setProperty('--tg-button-text-color', theme.button_text_color || '#ffffff');
      root.style.setProperty('--tg-secondary-bg-color', theme.secondary_bg_color || '#f1f1f1');

      // Применяем тему к body
      document.body.style.backgroundColor = theme.bg_color || '#ffffff';
      document.body.style.color = theme.text_color || '#000000';
      
      console.log('✅ Тема Telegram применена');
    } catch (error) {
      console.error('❌ Ошибка применения темы:', error);
    }
  }

  // Открыть ссылку (Telegram контакт)
  openTelegramLink(username: string): void {
    if (!this.webApp) {
      console.warn('⚠️ Telegram WebApp недоступен для открытия ссылки');
      // Fallback для обычного браузера
      window.open(`https://t.me/${username}`, '_blank');
      return;
    }

    try {
      this.webApp.openTelegramLink(`https://t.me/${username}`);
      console.log(`🔗 Открыта ссылка на пользователя: ${username}`);
    } catch (error) {
      console.error('❌ Ошибка открытия ссылки:', error);
      // Fallback
      window.open(`https://t.me/${username}`, '_blank');
    }
  }

  // Показать предупреждение
  showAlert(message: string): void {
    if (this.webApp) {
      try {
        this.webApp.showAlert(message);
        return;
      } catch (error) {
        console.error('❌ Ошибка показа alert через WebApp:', error);
      }
    }
    
    // Fallback для обычного браузера
    alert(message);
  }

  // Показать подтверждение
  showConfirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      if (this.webApp) {
        try {
          this.webApp.showConfirm(message, resolve);
          return;
        } catch (error) {
          console.error('❌ Ошибка показа confirm через WebApp:', error);
        }
      }
      
      // Fallback для обычного браузера
      resolve(confirm(message));
    });
  }

  // НОВОЕ: Получить информацию о платформе
  getPlatformInfo(): { platform: string; version: string; inTelegram: boolean } {
    if (!this.webApp) {
      return {
        platform: 'web',
        version: 'unknown',
        inTelegram: false
      };
    }

    return {
      platform: this.webApp.platform || 'unknown',
      version: this.webApp.version || 'unknown',
      inTelegram: this.isInTelegram()
    };
  }

  // НОВОЕ: Закрыть WebApp
  close(): void {
    if (this.webApp) {
      try {
        this.webApp.disableClosingConfirmation();
        // Telegram автоматически закроет приложение при вызове этого метода
        console.log('🔚 WebApp закрывается...');
      } catch (error) {
        console.error('❌ Ошибка закрытия WebApp:', error);
      }
    }
  }
}

// Создаем синглтон экземпляр
export const telegram = TelegramWebApp.getInstance();

// Дополнительные утилиты
export { tg };

// НОВОЕ: Функция для отладки
export const debugTelegram = () => {
  if (typeof window === 'undefined') {
    console.log('🔍 Telegram Debug: выполняется на сервере');
    return;
  }

  const info = {
    windowTelegram: !!window.Telegram,
    webApp: !!window.Telegram?.WebApp,
    initData: window.Telegram?.WebApp?.initData || 'отсутствует',
    initDataLength: window.Telegram?.WebApp?.initData?.length || 0,
    user: window.Telegram?.WebApp?.initDataUnsafe?.user || 'отсутствует',
    platform: window.Telegram?.WebApp?.platform || 'неизвестно',
    version: window.Telegram?.WebApp?.version || 'неизвестно',
    theme: window.Telegram?.WebApp?.themeParams || 'отсутствует'
  };

  console.log('🔍 Telegram WebApp Debug Info:', info);
  return info;
};
