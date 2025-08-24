/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Главное для Docker (мультистейдж/standalone runner):
  output: 'standalone',

  // Чтобы не упереться в sharp на Alpine (next/image будет без оптимизации)
  images: {
    unoptimized: true,
  },

  // Сборка не падает из-за линта/типов — как у тебя
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // Опционально: снять заголовок "X-Powered-By: Next.js"
  poweredByHeader: false,

  // experimental: {} оставляем пустым
};

module.exports = nextConfig;
