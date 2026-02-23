"use client";

import Link from "next/link";
import {
    AlertTriangle,
    BookOpen,
    Activity,
    ArrowRight,
} from "lucide-react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";

export default function DashboardPage() {
    const { orgSlug } = useOrg();

    return (
        <DashboardLayout>
            <div className="page-container">
                <div className="page-header">
                    <div>
                        <h1 className="page-title">Dashboard</h1>
                        <p className="page-subtitle">
                            Overview of your IT service management
                        </p>
                    </div>
                </div>

                <div className="dashboard-grid">
                    <Link href={`/${orgSlug}/incidents`} className="dashboard-card">
                        <div className="dashboard-card-icon dashboard-card-icon-red">
                            <AlertTriangle size={20} />
                        </div>
                        <div className="dashboard-card-body">
                            <h3 className="dashboard-card-title">Incidents</h3>
                            <p className="dashboard-card-desc">
                                Report, track, and resolve IT incidents
                            </p>
                        </div>
                        <ArrowRight size={16} className="dashboard-card-arrow" />
                    </Link>

                    <Link href={`/${orgSlug}/services`} className="dashboard-card">
                        <div className="dashboard-card-icon dashboard-card-icon-blue">
                            <BookOpen size={20} />
                        </div>
                        <div className="dashboard-card-body">
                            <h3 className="dashboard-card-title">Service Catalog</h3>
                            <p className="dashboard-card-desc">
                                Manage IT services and their operational status
                            </p>
                        </div>
                        <ArrowRight size={16} className="dashboard-card-arrow" />
                    </Link>

                    <div className="dashboard-card dashboard-card-static">
                        <div className="dashboard-card-icon dashboard-card-icon-green">
                            <Activity size={20} />
                        </div>
                        <div className="dashboard-card-body">
                            <h3 className="dashboard-card-title">System Status</h3>
                            <p className="dashboard-card-desc">
                                All systems operational
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
