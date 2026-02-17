"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/AuthProvider";
import AccountSettingsSidebar from "./AccountSettingsSidebar";
import {
    GeneralSection,
    ProfileSection,
    SessionsSection,
    LoginMethodsSection,
    DangerZoneSection,
} from "@/components/settings";
import type { UserProfile, ActiveSession } from "@/types/settings";

interface AccountSettingsPageProps {
    tab: string;
}

export default function AccountSettingsPage({ tab }: AccountSettingsPageProps) {
    const router = useRouter();
    const { logout, user } = useAuth();

    // State
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [sessions, setSessions] = useState<ActiveSession[]>([]);
    const [profileLoading, setProfileLoading] = useState(true);
    const [sessionsLoading, setSessionsLoading] = useState(true);
    const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

    // Toast helper
    const showToast = useCallback((message: string, type: "success" | "error" = "success") => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    }, []);

    // Derive effective profile — fall back to AuthProvider user if profile API fails
    const effectiveProfile: UserProfile | null = profile ?? (user ? {
        id: user.id,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        display_name: user.display_name,
        picture: user.picture,
        email_verified: user.email_verified,
        has_password: user.has_password,
    } : null);

    // Fetch profile
    const fetchProfile = useCallback(async () => {
        try {
            const res = await fetch("/api/account/profile");
            if (!res.ok) throw new Error("Failed to load profile");
            const data = await res.json();
            setProfile(data);
        } catch {
            // Will use AuthProvider user as fallback
        } finally {
            setProfileLoading(false);
        }
    }, []);

    // Fetch sessions
    const fetchSessions = useCallback(async () => {
        try {
            const res = await fetch("/api/account/sessions");
            if (!res.ok) throw new Error("Failed to load sessions");
            const data = await res.json();
            setSessions(data);
        } catch {
            showToast("Failed to load sessions", "error");
        } finally {
            setSessionsLoading(false);
        }
    }, [showToast]);

    useEffect(() => {
        fetchProfile();
        fetchSessions();
    }, [fetchProfile, fetchSessions]);

    // Mutations
    const handleUpdateName = async (name: string) => {
        const res = await fetch("/api/account/profile", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || "Failed to update name");
        }
        const updated = await res.json();
        setProfile(updated);
        showToast("Name updated");
    };

    const handleSetPassword = async (
        newPassword: string,
        confirmPassword: string,
        currentPassword?: string,
    ) => {
        const res = await fetch("/api/account/profile/password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                new_password: newPassword,
                confirm_password: confirmPassword,
                current_password: currentPassword || null,
            }),
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || "Failed to update password");
        }
        setProfile((prev) => prev ? { ...prev, has_password: true } : prev);
        showToast("Password updated");
    };

    const handleRevokeSession = async (sessionId: string) => {
        const res = await fetch(`/api/account/sessions/${sessionId}`, {
            method: "DELETE",
        });
        if (!res.ok) {
            showToast("Failed to revoke session", "error");
            return;
        }
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));
        showToast("Session revoked");
    };

    const handleLogoutAll = async () => {
        const res = await fetch("/api/account/logout-all", { method: "POST" });
        if (!res.ok) {
            showToast("Failed to log out all devices", "error");
            return;
        }
        showToast("All sessions revoked. Redirecting...");
        setTimeout(() => logout(), 1500);
    };

    const handleDeleteAccount = async () => {
        const res = await fetch("/api/account/profile", { method: "DELETE" });
        if (!res.ok) {
            showToast("Failed to delete account", "error");
            return;
        }
        showToast("Account deleted. Redirecting...");
        setTimeout(() => {
            logout();
            router.push("/");
        }, 1500);
    };

    return (
        <div className="settings-page">
            <div className="page-header">
                <h1 className="page-title">Settings</h1>
            </div>

            <div className="settings-page-body">
                <AccountSettingsSidebar />

                <div className="settings-content">
                    {tab === "general" && <GeneralSection />}

                    {tab === "account" && (
                        <div className="settings-section-content">
                            <ProfileSection
                                profile={effectiveProfile}
                                loading={profileLoading && !effectiveProfile}
                                onUpdateName={handleUpdateName}
                            />
                            <SessionsSection
                                sessions={sessions}
                                loading={sessionsLoading}
                                onRevoke={handleRevokeSession}
                                onLogoutAll={handleLogoutAll}
                            />
                            <LoginMethodsSection
                                email={effectiveProfile?.email || ""}
                                hasPassword={effectiveProfile?.has_password || false}
                                onSetPassword={handleSetPassword}
                            />
                            <DangerZoneSection
                                onDeleteAccount={handleDeleteAccount}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Toast notification */}
            {toast && (
                <div className={`settings-toast ${toast.type === "error" ? "settings-toast-error" : "settings-toast-success"}`}>
                    {toast.message}
                </div>
            )}
        </div>
    );
}
