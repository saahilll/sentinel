"use client";

import { useState } from "react";
import { Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";
import SettingsCard from "./SettingsCard";

interface LoginMethodsSectionProps {
    email: string;
    hasPassword: boolean;
    onSetPassword: (
        newPassword: string,
        confirmPassword: string,
        currentPassword?: string,
    ) => Promise<void>;
}

export default function LoginMethodsSection({
    email,
    hasPassword,
    onSetPassword,
}: LoginMethodsSectionProps) {
    const [showForm, setShowForm] = useState(false);
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showCurrent, setShowCurrent] = useState(false);
    const [showNew, setShowNew] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    const resetForm = () => {
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
        setError("");
        setShowForm(false);
    };

    const handleSubmit = async () => {
        if (newPassword.length < 8) {
            setError("Password must be at least 8 characters");
            return;
        }
        if (newPassword !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }
        setSaving(true);
        setError("");
        try {
            await onSetPassword(
                newPassword,
                confirmPassword,
                hasPassword ? currentPassword : undefined,
            );
            resetForm();
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : "Failed to update password";
            setError(msg);
        } finally {
            setSaving(false);
        }
    };

    return (
        <SettingsCard
            title="Login Methods"
            description="How you can sign in to your account"
        >
            <div className="login-methods">
                {/* Email — always active */}
                <div className="login-method-item">
                    <div className="login-method-icon">
                        <Mail size={18} />
                    </div>
                    <div className="login-method-info">
                        <p className="login-method-name">Email</p>
                        <p className="login-method-detail">{email}</p>
                    </div>
                    <span className="login-method-badge login-method-badge-active">
                        Active
                    </span>
                </div>

                {/* Password */}
                <div className="login-method-item-wrapper">
                    <div className="login-method-item">
                        <div className="login-method-icon">
                            <Lock size={18} />
                        </div>
                        <div className="login-method-info">
                            <p className="login-method-name">Password</p>
                            <p className="login-method-detail">
                                {hasPassword ? "Password is set" : "No password set"}
                            </p>
                        </div>
                        {!showForm && (
                            <button
                                className="settings-btn settings-btn-secondary settings-btn-sm"
                                onClick={() => setShowForm(true)}
                            >
                                {hasPassword ? "Change" : "Set password"}
                            </button>
                        )}
                    </div>

                    {showForm && (
                        <div className="password-form">
                            {hasPassword && (
                                <div className="password-field">
                                    <label className="password-label">Current password</label>
                                    <div className="password-input-wrapper">
                                        <input
                                            className="password-input"
                                            type={showCurrent ? "text" : "password"}
                                            value={currentPassword}
                                            onChange={(e) => setCurrentPassword(e.target.value)}
                                            placeholder="Enter current password"
                                        />
                                        <button
                                            className="password-toggle"
                                            type="button"
                                            onClick={() => setShowCurrent(!showCurrent)}
                                        >
                                            {showCurrent ? <EyeOff size={14} /> : <Eye size={14} />}
                                        </button>
                                    </div>
                                </div>
                            )}

                            <div className="password-field">
                                <label className="password-label">New password</label>
                                <div className="password-input-wrapper">
                                    <input
                                        className="password-input"
                                        type={showNew ? "text" : "password"}
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        placeholder="At least 8 characters"
                                    />
                                    <button
                                        className="password-toggle"
                                        type="button"
                                        onClick={() => setShowNew(!showNew)}
                                    >
                                        {showNew ? <EyeOff size={14} /> : <Eye size={14} />}
                                    </button>
                                </div>
                            </div>

                            <div className="password-field">
                                <label className="password-label">Confirm password</label>
                                <div className="password-input-wrapper">
                                    <input
                                        className="password-input"
                                        type={showConfirm ? "text" : "password"}
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="Confirm new password"
                                    />
                                    <button
                                        className="password-toggle"
                                        type="button"
                                        onClick={() => setShowConfirm(!showConfirm)}
                                    >
                                        {showConfirm ? <EyeOff size={14} /> : <Eye size={14} />}
                                    </button>
                                </div>
                            </div>

                            {error && <p className="password-error">{error}</p>}

                            <div className="password-actions">
                                <button
                                    className="settings-btn settings-btn-ghost settings-btn-sm"
                                    onClick={resetForm}
                                    disabled={saving}
                                >
                                    Cancel
                                </button>
                                <button
                                    className="settings-btn settings-btn-primary settings-btn-sm"
                                    onClick={handleSubmit}
                                    disabled={saving || !newPassword || !confirmPassword}
                                >
                                    {saving ? (
                                        <span className="btn-loading">
                                            <Loader2 size={14} className="animate-spin" />
                                            Saving...
                                        </span>
                                    ) : hasPassword ? (
                                        "Change password"
                                    ) : (
                                        "Set password"
                                    )}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </SettingsCard>
    );
}
