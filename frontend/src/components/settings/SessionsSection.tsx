"use client";

import { useState } from "react";
import { Monitor, Smartphone, Loader2 } from "lucide-react";
import SettingsCard from "./SettingsCard";
import type { ActiveSession } from "@/types/settings";

interface SessionsSectionProps {
    sessions: ActiveSession[];
    loading: boolean;
    onRevoke: (sessionId: string) => Promise<void>;
    onLogoutAll: () => Promise<void>;
}

function parseDevice(userAgent: string): { label: string; isMobile: boolean } {
    const ua = userAgent.toLowerCase();
    if (ua.includes("mobile") || ua.includes("android") || ua.includes("iphone")) {
        return { label: "Mobile Device", isMobile: true };
    }
    if (ua.includes("chrome")) return { label: "Chrome", isMobile: false };
    if (ua.includes("firefox")) return { label: "Firefox", isMobile: false };
    if (ua.includes("safari")) return { label: "Safari", isMobile: false };
    if (ua.includes("edge")) return { label: "Edge", isMobile: false };
    if (ua.includes("postman")) return { label: "Postman", isMobile: false };
    if (ua.includes("python")) return { label: "Python Client", isMobile: false };
    return { label: userAgent.slice(0, 50) || "Unknown Device", isMobile: false };
}

function timeAgo(date: string): string {
    const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
    if (seconds < 60) return "Just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

export default function SessionsSection({
    sessions,
    loading,
    onRevoke,
    onLogoutAll,
}: SessionsSectionProps) {
    const [revokingId, setRevokingId] = useState<string | null>(null);
    const [loggingOutAll, setLoggingOutAll] = useState(false);

    const handleRevoke = async (id: string) => {
        setRevokingId(id);
        try {
            await onRevoke(id);
        } finally {
            setRevokingId(null);
        }
    };

    const handleLogoutAll = async () => {
        setLoggingOutAll(true);
        try {
            await onLogoutAll();
        } finally {
            setLoggingOutAll(false);
        }
    };

    const logoutAllBtn = sessions.length > 1 ? (
        <button
            className="settings-btn settings-btn-danger-outline settings-btn-sm"
            onClick={handleLogoutAll}
            disabled={loggingOutAll}
        >
            {loggingOutAll ? (
                <span className="btn-loading">
                    <Loader2 size={14} className="animate-spin" />
                    Logging out...
                </span>
            ) : (
                "Log out all devices"
            )}
        </button>
    ) : undefined;

    return (
        <SettingsCard
            title="Active Sessions"
            description="Devices where you're logged in"
            action={logoutAllBtn}
        >
            {loading ? (
                <div className="sessions-loading">
                    <Loader2 size={16} className="animate-spin" />
                    Loading sessions...
                </div>
            ) : sessions.length === 0 ? (
                <div className="sessions-empty">No active sessions</div>
            ) : (
                <div className="sessions-list">
                    {sessions.map((session) => {
                        const { label, isMobile } = parseDevice(session.device_info);
                        const Icon = isMobile ? Smartphone : Monitor;
                        return (
                            <div key={session.id} className="session-item">
                                <div className="session-icon">
                                    <Icon size={18} />
                                </div>
                                <div className="session-info">
                                    <p className="session-device">{label}</p>
                                    <p className="session-details">
                                        <span>{timeAgo(session.last_used_at)}</span>
                                        {session.ip_address && (
                                            <span>{session.ip_address}</span>
                                        )}
                                    </p>
                                </div>
                                {session.is_current ? (
                                    <span className="session-current-badge">
                                        This device
                                    </span>
                                ) : (
                                    <button
                                        className="settings-btn settings-btn-ghost settings-btn-sm"
                                        onClick={() => handleRevoke(session.id)}
                                        disabled={revokingId === session.id}
                                    >
                                        {revokingId === session.id ? (
                                            <Loader2 size={12} className="animate-spin" />
                                        ) : (
                                            "Revoke"
                                        )}
                                    </button>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </SettingsCard>
    );
}
