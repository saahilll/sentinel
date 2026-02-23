"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";

const sectionMap: Record<string, string> = {
    dashboard: "Dashboard",
    incidents: "Incidents",
    services: "Services",
    settings: "Settings",
};

export default function Breadcrumbs() {
    const pathname = usePathname();

    const parts = pathname.split("/").filter(Boolean);
    const section = parts[0];
    const sectionName = section ? (sectionMap[section] || section.charAt(0).toUpperCase() + section.slice(1)) : null;
    const subSection = parts.length > 1 ? parts.slice(1).join(" / ") : null;

    return (
        <nav className="breadcrumbs" aria-label="Breadcrumb">
            <ol className="breadcrumbs-list">
                <li className="breadcrumbs-item">
                    <Link href="/dashboard" className="breadcrumbs-link">Home</Link>
                </li>
                {sectionName && (
                    <>
                        <ChevronRight size={14} className="breadcrumbs-separator" />
                        <li className="breadcrumbs-item">
                            <span className="breadcrumbs-current">{sectionName}</span>
                        </li>
                    </>
                )}
                {subSection && (
                    <>
                        <ChevronRight size={14} className="breadcrumbs-separator" />
                        <li className="breadcrumbs-item">
                            <span className="breadcrumbs-current">
                                {subSection.charAt(0).toUpperCase() + subSection.slice(1)}
                            </span>
                        </li>
                    </>
                )}
            </ol>
        </nav>
    );
}
