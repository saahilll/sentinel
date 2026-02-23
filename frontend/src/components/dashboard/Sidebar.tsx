"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    AlertTriangle,
    BookOpen,
    LayoutDashboard,
    Settings,
    Bell,
    CircleHelpIcon,
    PanelLeftClose,
    PanelLeft,
} from "lucide-react";
import { useSidebar } from "@/components/providers/SidebarProvider";
import { useOrg } from "@/components/providers/OrgProvider";

export default function Sidebar() {
    const pathname = usePathname();
    const { collapsed, toggleSidebar } = useSidebar();
    const { orgSlug } = useOrg();

    const base = `/${orgSlug}`;

    const navigation = [
        { name: "Dashboard", href: `${base}/dashboard`, icon: LayoutDashboard },
        { name: "Incidents", href: `${base}/incidents`, icon: AlertTriangle },
        { name: "Services", href: `${base}/services`, icon: BookOpen },
        { name: "Settings", href: `${base}/settings/general`, icon: Settings },
    ];

    const secondaryNavigation = [
        { name: "Notifications", href: `${base}/notifications`, icon: Bell },
        { name: "Help & Support", href: `${base}/help`, icon: CircleHelpIcon },
    ];

    return (
        <aside className={`sidebar ${collapsed ? "sidebar-collapsed" : ""}`}>
            <div className="sidebar-header">
                <Link href={`${base}/dashboard`} className="logo" title="Dashboard">
                    {collapsed ? (
                        <div className="logo-icon-collapsed bg-white rounded-md flex items-center justify-center font-bold text-black text-xs">S</div>
                    ) : (
                        <span className="logo-text">Sentinel</span>
                    )}
                </Link>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    {!collapsed && <span className="nav-section-title">Main</span>}
                    <ul className="nav-list">
                        {navigation.map((item) => {
                            const isActive =
                                item.name === "Settings"
                                    ? pathname.includes("/settings")
                                    : pathname === item.href || pathname.startsWith(item.href + "/");
                            return (
                                <li key={item.name}>
                                    <Link
                                        href={item.href}
                                        className={`nav-item ${isActive ? "nav-item-active" : ""}`}
                                        title={collapsed ? item.name : undefined}
                                    >
                                        <item.icon size={16} className="nav-icon" />
                                        {!collapsed && <span>{item.name}</span>}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </div>

                <div className="nav-section">
                    {!collapsed && <span className="nav-section-title">Support</span>}
                    <ul className="nav-list">
                        {secondaryNavigation.map((item) => {
                            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                            return (
                                <li key={item.name}>
                                    <Link
                                        href={item.href}
                                        className={`nav-item ${isActive ? "nav-item-active" : ""}`}
                                        title={collapsed ? item.name : undefined}
                                    >
                                        <item.icon size={16} className="nav-icon" />
                                        {!collapsed && <span>{item.name}</span>}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-actions">
                    <button
                        className="sidebar-action-btn"
                        onClick={toggleSidebar}
                        title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
                    >
                        {collapsed ? <PanelLeft size={16} /> : <PanelLeftClose size={16} />}
                        {!collapsed && <span>Collapse</span>}
                    </button>
                </div>
            </div>
        </aside>
    );
}
