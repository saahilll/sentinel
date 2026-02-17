"use client";

interface SettingsCardProps {
    title: string;
    description?: string;
    variant?: "default" | "danger";
    action?: React.ReactNode;
    children: React.ReactNode;
}

export default function SettingsCard({
    title,
    description,
    variant = "default",
    action,
    children,
}: SettingsCardProps) {
    return (
        <div className={`settings-card ${variant === "danger" ? "settings-card-danger" : ""}`}>
            <div className="settings-card-header">
                <div className="settings-card-header-text">
                    <div className="settings-card-title">{title}</div>
                    {description && (
                        <div className="settings-card-description">{description}</div>
                    )}
                </div>
                {action}
            </div>
            <div className="settings-card-content">{children}</div>
        </div>
    );
}
