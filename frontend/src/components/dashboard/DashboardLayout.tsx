"use client";

import { useAuth } from "@/components/providers/AuthProvider";
import { SidebarProvider, useSidebar } from "@/components/providers/SidebarProvider";
import { useOrg } from "@/components/providers/OrgProvider";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import { useEffect } from "react";

interface DashboardLayoutProps {
    children: React.ReactNode;
}

function DashboardInner({ children }: DashboardLayoutProps) {
    const { isLoading: authLoading, isAuthenticated } = useAuth();
    const { collapsed } = useSidebar();
    const { isLoading: orgLoading, org } = useOrg();

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            window.location.href = "/login";
        }
    }, [authLoading, isAuthenticated]);

    if (authLoading || orgLoading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner" />
                <p>Loading...</p>
            </div>
        );
    }

    if (!isAuthenticated || !org) {
        return null;
    }

    return (
        <div className="dashboard-container">
            <Sidebar />
            <div className={`main-wrapper ${collapsed ? "main-wrapper-expanded" : ""}`}>
                <Navbar />
                <main className="main-content">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    return (
        <SidebarProvider>
            <DashboardInner>{children}</DashboardInner>
        </SidebarProvider>
    );
}
