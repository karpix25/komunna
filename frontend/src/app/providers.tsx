// app/providers.tsx
"use client";

import { TwaProvider } from "@/context/TwaContext";

export default function Providers({ children }: { children: React.ReactNode }) {
  return <TwaProvider>{children}</TwaProvider>;
}
