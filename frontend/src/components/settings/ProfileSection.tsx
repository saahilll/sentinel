"use client";

import { useState } from "react";
import { Pencil, Check, X } from "lucide-react";
import UserAvatar from "@/components/shared/UserAvatar";
import SettingsCard from "./SettingsCard";
import type { UserProfile } from "@/types/settings";

interface ProfileSectionProps {
    profile: UserProfile | null;
    loading: boolean;
    onUpdateName: (name: string) => Promise<void>;
}

export default function ProfileSection({
    profile,
    loading,
    onUpdateName,
}: ProfileSectionProps) {
    const [editing, setEditing] = useState(false);
    const [name, setName] = useState("");
    const [saving, setSaving] = useState(false);

    const startEditing = () => {
        setName(profile?.display_name || "");
        setEditing(true);
    };

    const cancelEditing = () => {
        setEditing(false);
        setName("");
    };

    const handleSave = async () => {
        if (!name.trim()) return;
        setSaving(true);
        try {
            await onUpdateName(name.trim());
            setEditing(false);
        } finally {
            setSaving(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") handleSave();
        if (e.key === "Escape") cancelEditing();
    };

    if (loading) {
        return (
            <SettingsCard title="Profile" description="Your personal information">
                <div className="profile-skeleton">
                    <div className="profile-avatar-skeleton" />
                    <div className="profile-info-skeleton">
                        <div className="skeleton-line skeleton-line-lg" />
                        <div className="skeleton-line skeleton-line-md" />
                    </div>
                </div>
            </SettingsCard>
        );
    }

    if (!profile) return null;

    return (
        <SettingsCard title="Profile" description="Your personal information">
            <div className="profile-header">
                <UserAvatar
                    picture={profile.picture ?? undefined}
                    name={profile.display_name}
                    email={profile.email}
                    size="lg"
                />
                <div className="profile-info">
                    {editing ? (
                        <div className="profile-edit-row">
                            <input
                                className="profile-edit-input"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                onKeyDown={handleKeyDown}
                                autoFocus
                                disabled={saving}
                            />
                            <div className="profile-edit-actions">
                                <button
                                    className="settings-btn settings-btn-primary settings-btn-sm settings-btn-icon"
                                    onClick={handleSave}
                                    disabled={saving || !name.trim()}
                                >
                                    <Check size={14} />
                                </button>
                                <button
                                    className="settings-btn settings-btn-ghost settings-btn-sm settings-btn-icon"
                                    onClick={cancelEditing}
                                    disabled={saving}
                                >
                                    <X size={14} />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="profile-name">
                            <span
                                className="profile-name-editable"
                                onClick={startEditing}
                            >
                                {profile.display_name}
                                <Pencil size={12} className="profile-name-pencil" />
                            </span>
                        </div>
                    )}
                    <div className="profile-email">{profile.email}</div>
                </div>
            </div>
        </SettingsCard>
    );
}
