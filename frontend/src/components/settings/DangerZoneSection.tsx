"use client";

import { useState } from "react";
import { Trash2 } from "lucide-react";
import SettingsCard from "./SettingsCard";
import ConfirmDialog from "./ConfirmDialog";

interface DangerZoneSectionProps {
    onDeleteAccount: () => Promise<void>;
}

export default function DangerZoneSection({
    onDeleteAccount,
}: DangerZoneSectionProps) {
    const [showDialog, setShowDialog] = useState(false);
    const [deleting, setDeleting] = useState(false);

    const handleDelete = async () => {
        setDeleting(true);
        try {
            await onDeleteAccount();
        } finally {
            setDeleting(false);
            setShowDialog(false);
        }
    };

    return (
        <>
            <SettingsCard
                title="Danger Zone"
                description="Irreversible actions"
                variant="danger"
            >
                <div className="danger-zone-content">
                    <div className="danger-zone-item">
                        <div className="danger-zone-info">
                            <div className="danger-zone-label">Delete account</div>
                            <div className="danger-zone-description">
                                Permanently delete your account and all associated data.
                                This action cannot be undone.
                            </div>
                        </div>
                        <button
                            className="settings-btn settings-btn-danger-outline"
                            onClick={() => setShowDialog(true)}
                        >
                            <Trash2 size={14} />
                            Delete account
                        </button>
                    </div>
                </div>
            </SettingsCard>

            <ConfirmDialog
                open={showDialog}
                onClose={() => setShowDialog(false)}
                onConfirm={handleDelete}
                title="Delete your account?"
                description="This will permanently delete your account, revoke all sessions, and remove your data. This cannot be undone."
                confirmText="DELETE"
                confirmLabel="Delete my account"
                loading={deleting}
            />
        </>
    );
}
