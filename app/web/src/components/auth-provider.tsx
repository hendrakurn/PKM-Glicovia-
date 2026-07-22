"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api } from "@/lib/api/client";
import type { AuthProfile, AuthResponse } from "@/lib/api/types";

const TOKEN_KEY = "glicovia.accessToken";

type AuthStatus = "booting" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  token: string | null;
  profile: AuthProfile | null;
  status: AuthStatus;
  signIn: (response: AuthResponse) => void;
  signOut: () => void;
  refreshProfile: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [profile, setProfile] = useState<AuthProfile | null>(null);
  const [status, setStatus] = useState<AuthStatus>("booting");

  const clearSession = useCallback(() => {
    if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setProfile(null);
    setStatus("unauthenticated");
  }, []);

  const refreshProfile = useCallback(async () => {
    const activeToken = token ?? (typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null);
    if (!activeToken) {
      clearSession();
      return;
    }

    try {
      setStatus("booting");
      const nextProfile = await api.me(activeToken);
      setToken(activeToken);
      setProfile(nextProfile);
      setStatus("authenticated");
    } catch {
      clearSession();
    }
  }, [clearSession, token]);

  useEffect(() => {
    let active = true;

    async function loadStoredSession() {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (!storedToken) {
        if (active) setStatus("unauthenticated");
        return;
      }

      try {
        const nextProfile = await api.me(storedToken);
        if (!active) return;
        setToken(storedToken);
        setProfile(nextProfile);
        setStatus("authenticated");
      } catch {
        if (active) clearSession();
      }
    }

    void loadStoredSession();
    return () => {
      active = false;
    };
  }, [clearSession]);

  useEffect(() => {
    const onUnauthorized = () => clearSession();
    window.addEventListener("glicovia:unauthorized", onUnauthorized);
    return () => window.removeEventListener("glicovia:unauthorized", onUnauthorized);
  }, [clearSession]);

  const signIn = useCallback((response: AuthResponse) => {
    localStorage.setItem(TOKEN_KEY, response.accessToken);
    setToken(response.accessToken);
    setProfile({ user: response.user, subject: response.subject });
    setStatus("authenticated");
  }, []);

  const value = useMemo(
    () => ({ token, profile, status, signIn, signOut: clearSession, refreshProfile }),
    [clearSession, profile, refreshProfile, signIn, status, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
