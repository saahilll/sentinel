"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Settings, User } from "lucide-react";

const tabs = [
    { id: "general", label: "General", icon: Settings, href: "/settings/general" },
    { id: "account", label: "Account", icon: User, href: "/settings/account" },
];

export default function AccountSettingsSidebar() {
    const pathname = usePathname();
    const currentTab = pathname?.split("/settings/")[1] || "general";

    return (
        <aside className="settings-sidebar">
            <nav className="settings-sidebar-nav">
                {tabs.map((tab) => (
                    <Link
                        key={tab.id}
                        href={tab.href}
                        className={`settings-sidebar-item ${currentTab === tab.id ? "active" : ""}`}
                    >
                        <tab.icon size={16} />
                        <span>{tab.label}</span>
                    </Link>
                ))}
            </nav>
        </aside>
    );
}
