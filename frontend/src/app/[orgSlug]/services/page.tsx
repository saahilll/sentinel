"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Plus, Loader2, BookOpen, RefreshCw } from "lucide-react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";
import type { ServiceListItem, ServiceStatus, ServiceTier } from "@/types/service";

const STATUS_BADGES: Record<ServiceStatus, { label: string; className: string }> = {
    operational: { label: "Operational", className: "badge-success" },
    degraded: { label: "Degraded", className: "badge-warning" },
    partial_outage: { label: "Partial Outage", className: "badge-danger" },
    major_outage: { label: "Major Outage", className: "badge-critical" },
    maintenance: { label: "Maintenance", className: "badge-info" },
};

const TIER_LABELS: Record<ServiceTier, string> = {
    critical: "Critical",
    high: "High",
    medium: "Medium",
    low: "Low",
};

export default function ServicesPage() {
    const router = useRouter();
    const { orgSlug, isLoading: orgLoading } = useOrg();
    const [services, setServices] = useState<ServiceListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchServices = async () => {
        if (!orgSlug) return;
        setIsLoading(true);
        try {
            const res = await fetch(`/api/proxy/orgs/${orgSlug}/services`, {
                credentials: "include",
            });
            if (res.ok) {
                setServices(await res.json());
            } else {
                setError("Failed to load services");
            }
        } catch {
            setError("Failed to load services");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (!orgLoading && orgSlug) fetchServices();
    }, [orgSlug, orgLoading]);

    return (
        <DashboardLayout>
            <div className="page-container">
                <div className="page-header">
                    <div>
                        <h1 className="page-title">Service Catalog</h1>
                        <p className="page-subtitle">Manage your IT services and their operational status</p>
                    </div>
                    <div className="page-actions">
                        <button className="btn btn-ghost" onClick={fetchServices} title="Refresh">
                            <RefreshCw size={16} />
                        </button>
                        <Link href={`/${orgSlug}/services/new`} className="btn btn-primary">
                            <Plus size={16} />
                            Add Service
                        </Link>
                    </div>
                </div>

                {isLoading || orgLoading ? (
                    <div className="page-loading">
                        <Loader2 size={24} className="animate-spin" />
                        <span>Loading services...</span>
                    </div>
                ) : error ? (
                    <div className="page-error">{error}</div>
                ) : services.length === 0 ? (
                    <div className="page-empty">
                        <BookOpen size={48} strokeWidth={1} />
                        <h2>No services yet</h2>
                        <p>Create your first service to start building your service catalog.</p>
                        <Link href={`/${orgSlug}/services/new`} className="btn btn-primary">
                            <Plus size={16} />
                            Create Service
                        </Link>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Status</th>
                                    <th>Tier</th>
                                    <th>Category</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {services.map((svc) => {
                                    const badge = STATUS_BADGES[svc.status];
                                    return (
                                        <tr
                                            key={svc.id}
                                            className="table-row-clickable"
                                            onClick={() => router.push(`/${orgSlug}/services/${svc.id}`)}
                                        >
                                            <td className="table-cell-primary">{svc.name}</td>
                                            <td>
                                                <span className={`badge ${badge.className}`}>
                                                    {badge.label}
                                                </span>
                                            </td>
                                            <td>{TIER_LABELS[svc.tier]}</td>
                                            <td>{svc.category || "—"}</td>
                                            <td className="table-cell-muted">
                                                {new Date(svc.created_at).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
