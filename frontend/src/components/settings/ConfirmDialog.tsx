"use client";

import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";

interface ConfirmDialogProps {
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    description: string;
    confirmText?: string;
    confirmLabel?: string;
    loading?: boolean;
}

export default function ConfirmDialog({
    open,
    onClose,
    onConfirm,
    title,
    description,
    confirmText = "DELETE",
    confirmLabel = "Delete account",
    loading = false,
}: ConfirmDialogProps) {
    const [input, setInput] = useState("");

    if (!open) return null;

    const isConfirmed = input === confirmText;

    return (
        <div className="dialog-overlay" onClick={onClose}>
            <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
                <button className="dialog-close" onClick={onClose}>
                    <X size={16} />
                </button>

                <div className="dialog-header">
                    <div className="dialog-icon-danger">
                        <AlertTriangle size={24} />
                    </div>
                    <div className="dialog-title">{title}</div>
                    <div className="dialog-description">{description}</div>
                </div>

                <div className="dialog-input-section">
                    <label className="dialog-input-label">
                        Type <strong>{confirmText}</strong> to confirm
                    </label>
                    <input
                        className="dialog-input"
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={confirmText}
                        autoFocus
                    />
                </div>

                <div className="dialog-footer">
                    <button
                        className="settings-btn settings-btn-secondary"
                        onClick={onClose}
                        disabled={loading}
                    >
                        Cancel
                    </button>
                    <button
                        className="settings-btn settings-btn-danger"
                        onClick={onConfirm}
                        disabled={!isConfirmed || loading}
                    >
                        {loading ? (
                            <span className="btn-loading">
                                <span className="btn-spinner" />
                                Deleting...
                            </span>
                        ) : (
                            confirmLabel
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
