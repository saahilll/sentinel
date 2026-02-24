"use client";

import { use } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { useOrg } from "@/components/providers/OrgProvider";
import { AccountSettingsPage } from "@/components/account";
import Navbar from "@/components/dashboard/Navbar";
import Link from "next/link";

export default function SettingsTabPage({
    params,
}: {
    params: Promise<{ tab: string }>;
}) {
    const { tab } = use(params);
    const { isLoading } = useAuth();
    const { orgSlug } = useOrg();

    if (isLoading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner" />
                <p>Loading...</p>
            </div>
        );
    }

    return (
        <div className="standalone-layout">
            <header className="standalone-topbar">
                <div className="standalone-topbar-left">
                    <Link href={`/${orgSlug}/dashboard`} className="standalone-logo">
                        <span className="standalone-logo-text">Sentinel</span>
                    </Link>
                </div>
                <Navbar />
            </header>
            <main className="standalone-content">
                <AccountSettingsPage tab={tab} />
            </main>
        </div>
    );
}
