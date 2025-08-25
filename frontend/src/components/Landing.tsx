// components/Landing.tsx
export default function Landing() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center px-6">
        <div className="mb-8">
          <h1 className="text-6xl md:text-8xl font-bold text-indigo-600 mb-4">
            Kommuna
          </h1>
          <div className="w-24 h-1 bg-indigo-600 mx-auto rounded-full"></div>
        </div>
        <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-md mx-auto">
          Платформа для обучения в Telegram сообществах
        </p>
        <div className="inline-flex items-center px-6 py-3 text-sm text-indigo-600 bg-white rounded-full shadow-lg">
          <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
          Скоро запуск
        </div>
      </div>
    </main>
  );
}
