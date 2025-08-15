// Zustand stores for state management

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, AuthTokens } from '@/types'

// Auth Store
interface AuthStore {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  login: (user: User, tokens: AuthTokens) => void
  logout: () => void
  updateUser: (userData: Partial<User>) => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      
      login: (user, tokens) => {
        set({
          user,
          tokens,
          isAuthenticated: true,
        })
      },
      
      logout: () => {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
        })
      },
      
      updateUser: (userData) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData }
          })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// App Store for general app state
interface AppStore {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  toggleTheme: () => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarOpen: false,
      
      toggleTheme: () => {
        set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light'
        }))
      },
      
      toggleSidebar: () => {
        set((state) => ({
          sidebarOpen: !state.sidebarOpen
        }))
      },
      
      setSidebarOpen: (open) => {
        set({ sidebarOpen: open })
      },
    }),
    {
      name: 'app-storage',
    }
  )
)
