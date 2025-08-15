'use client'

import React from 'react'
import { telegram } from '@/lib/telegram'

interface TelegramButtonProps {
  children: React.ReactNode
  onClick?: () => void
  username?: string
  variant?: 'primary' | 'secondary'
  className?: string
  disabled?: boolean
}

export function TelegramButton({
  children,
  onClick,
  username,
  variant = 'primary',
  className = '',
  disabled = false
}: TelegramButtonProps) {
  const handleClick = () => {
    if (disabled) return
    
    if (username) {
      telegram.openTelegramLink(username)
    } else if (onClick) {
      onClick()
    }
  }

  const buttonClass = variant === 'primary' ? 'tg-main-button' : 'tg-secondary-button'

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`${buttonClass} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  )
}
