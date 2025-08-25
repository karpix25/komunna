// context/TwaContext.tsx
"use client";

import { createContext, useContext, useEffect, useState } from "react";
import WebApp from "@twa-dev/sdk";
import { setupWebView, waitForInitData } from "@/lib/twa";

type TwaCtx = { initData: string | null; platform: string | null };
const Ctx = createContext<TwaCtx>({ initData: null, platform: null });

export function TwaProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<TwaCtx>({ initData: null, platform: null });

  useEffect(() => {
    setupWebView();
    (async () => {
      const id = await waitForInitData();
      setState({ initData: id, platform: WebApp?.platform ?? null });
    })();
  }, []);

  return <Ctx.Provider value={state}>{children}</Ctx.Provider>;
}

export function useTwa() {
  return useContext(Ctx);
}
