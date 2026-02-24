"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect, useRef, useCallback } from "react";
import {
    AlertTriangle,
    BookOpen,
    LayoutDashboard,
    Settings,
    Bell,
    CircleHelpIcon,
    PanelLeftClose,
    PanelLeft,
    ChevronsUpDown,
    Check,
    Plus,
} from "lucide-react";
import { useSidebar } from "@/components/providers/SidebarProvider";
import { useOrg } from "@/components/providers/OrgProvider";

interface OrgOption {
    id: string;
    name: string;
    slug: string;
    role: string;
}

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const { collapsed, toggleSidebar } = useSidebar();
    const { orgSlug } = useOrg();

    const [orgs, setOrgs] = useState<OrgOption[]>([]);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetch("/api/user/organizations", { credentials: "include" })
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                if (data) {
                    const list: OrgOption[] = Array.isArray(data) ? data : (data.organizations || []);
                    setOrgs(list);
                }
            })
            .catch(() => {});
    }, []);

    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSwitchOrg = useCallback(
        (slug: string) => {
            setDropdownOpen(false);
            if (slug === orgSlug) return;
            // Try to preserve current section (e.g. /dashboard, /incidents)
            const afterSlug = pathname.replace(`/${orgSlug}`, "");
            router.push(`/${slug}${afterSlug || "/dashboard"}`);
        },
        [orgSlug, pathname, router]
    );

    const currentOrg = orgs.find((o) => o.slug === orgSlug);
    const currentOrgName = currentOrg?.name || orgSlug;
    const currentAvatar = (currentOrgName.charAt(0) || "S").toUpperCase();

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

            {/* Org Switcher */}
            <div className="app-switcher" ref={dropdownRef}>
                <button
                    className="app-switcher-trigger"
                    onClick={() => setDropdownOpen((prev) => !prev)}
                    title={collapsed ? currentOrgName : undefined}
                >
                    <span className="app-switcher-avatar">{currentAvatar}</span>
                    {!collapsed && (
                        <>
                            <span className="app-switcher-label">{currentOrgName}</span>
                            <ChevronsUpDown size={14} className="app-switcher-icon" />
                        </>
                    )}
                </button>

                {dropdownOpen && (
                    <div className="app-switcher-dropdown">
                        <div className="app-switcher-section-label">Organizations</div>
                        <div className="app-switcher-list">
                            {orgs.map((org) => {
                                const isActive = org.slug === orgSlug;
                                return (
                                    <button
                                        key={org.id}
                                        className={`app-switcher-option ${isActive ? "app-switcher-option-active" : ""}`}
                                        onClick={() => handleSwitchOrg(org.slug)}
                                    >
                                        <span className="app-switcher-option-avatar">
                                            {(org.name.charAt(0) || "O").toUpperCase()}
                                        </span>
                                        <span className="app-switcher-option-name">{org.name}</span>
                                        {isActive && <Check size={14} className="app-switcher-check" />}
                                    </button>
                                );
                            })}
                        </div>
                        <div className="app-switcher-footer">
                            <Link
                                href="/create-org"
                                className="app-switcher-action"
                                onClick={() => setDropdownOpen(false)}
                            >
                                <Plus size={14} />
                                <span>Create organization</span>
                            </Link>
                        </div>
                    </div>
                )}
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
