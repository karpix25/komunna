"use client";
export const dynamic = "force-dynamic"; // не пререндерить на билде

import { useTwa } from "@/context/TwaContext";
import { useBootstrap } from "@/hooks/useBootstrap";
import Landing from "@/components/Landing";
import JsonBlock from "@/components/JsonBlock";

export default function Home() {
  const { initData } = useTwa();

  // нет initData — просто лендинг
  if (!initData) return <Landing />;

  // есть initData — грузим bootstrap
  const { bootstrap, error, loading } = useBootstrap(initData);

  return (
    <main className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-6 md:p-8">
        <h2 className="text-2xl font-bold text-indigo-600 mb-4">Bootstrap</h2>

        {loading && <div>Загрузка…</div>}
        {error && (
          <div className="text-red-600">
            Ошибка: {error.message || "Неизвестная ошибка"}
          </div>
        )}
        {bootstrap && <JsonBlock value={bootstrap} />}
      </div>
    </main>
  );
}
