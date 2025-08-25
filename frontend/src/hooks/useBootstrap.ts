"use client";

import { useCallback, useEffect, useState } from "react";
import { request } from "@/lib/request";
import type { BootstrapResponse } from "@/types/bootstrap";

export function useBootstrap(initData: string | null) {
  const [data, setData] = useState<BootstrapResponse | null>(null);
  const [error, setError] = useState<Error | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(false);

  const load = useCallback(async () => {
    if (!initData) return;
    setLoading(true);
    setError(undefined);
    try {
      const res = await request.get<BootstrapResponse>("/api/v1/auth/me/bootstrap", {
        initData,
      });
      setData(res);
    } catch (e: any) {
      setError(e);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [initData]);

  useEffect(() => {
    if (initData) load();
  }, [initData, load]);

  return { bootstrap: data, error, loading, refresh: load };
}
