/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Убираем проблемные настройки
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Исправляем предупреждения
  experimental: {
    // serverActions убираем - теперь включены по умолчанию
  },
  // Убираем проблемную переменную
  // env: {
  //   CUSTOM_KEY: process.env.CUSTOM_KEY,
  // },
}

module.exports = nextConfig
