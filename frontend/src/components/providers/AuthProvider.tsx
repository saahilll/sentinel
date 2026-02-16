"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { clearSession, isAuthenticated as checkAuth } from "@/lib/session";

interface AuthUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    display_name: string;
    picture: string;
    email_verified: boolean;
    has_password: boolean;
}

interface AuthContextType {
    user: AuthUser | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    refreshUser: () => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    refreshUser: async () => { },
    logout: async () => { },
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    const fetchUser = useCallback(async () => {
        try {
            if (!checkAuth()) {
                setUser(null);
                setIsLoading(false);
                return;
            }

            // Uses api instance which has the auto-refresh interceptor
            const response = await api.get("/api/auth/me");
            setUser(response.data);
        } catch {
            setUser(null);
            clearSession();
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const refreshUser = useCallback(async () => {
        await fetchUser();
    }, [fetchUser]);

    const logout = useCallback(async () => {
        try {
            const refreshToken = typeof window !== "undefined"
                ? localStorage.getItem("refresh_token")
                : null;

            if (refreshToken) {
                await api.post("/api/auth/logout", {
                    refresh_token: refreshToken,
                });
            }
        } catch {
            // Ignore logout errors — we clear the session anyway
        } finally {
            clearSession();
            setUser(null);
            router.push("/auth/login");
        }
    }, [router]);

    return (
        <AuthContext.Provider
            value={{
                user,
                isLoading,
                isAuthenticated: user !== null,
                refreshUser,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
