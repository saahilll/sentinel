"use client";

import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "@/components/providers/ThemeProvider";
import SettingsCard from "./SettingsCard";

type ThemeValue = "light" | "dark" | "system";

const themeOptions: { value: ThemeValue; label: string; icon: React.ElementType }[] = [
    { value: "light", label: "Light", icon: Sun },
    { value: "dark", label: "Dark", icon: Moon },
    { value: "system", label: "System", icon: Monitor },
];

export default function GeneralSection() {
    const { theme, setTheme } = useTheme();

    return (
        <div className="settings-section-content">
            <SettingsCard title="Appearance" description="Choose your preferred theme">
                <div className="theme-options">
                    {themeOptions.map((opt) => (
                        <button
                            key={opt.value}
                            className={`theme-option ${theme === opt.value ? "active" : ""}`}
                            onClick={() => setTheme(opt.value)}
                        >
                            <div className="theme-option-icon">
                                <opt.icon size={24} />
                            </div>
                            <span className="theme-option-label">{opt.label}</span>
                        </button>
                    ))}
                </div>
            </SettingsCard>
        </div>
    );
}
