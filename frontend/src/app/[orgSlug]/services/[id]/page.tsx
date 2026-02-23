"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { ArrowLeft, Loader2, ExternalLink } from "lucide-react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";
import type { Service, ServiceStatus } from "@/types/service";

const STATUS_BADGES: Record<ServiceStatus, { label: string; className: string }> = {
    operational: { label: "Operational", className: "badge-success" },
    degraded: { label: "Degraded", className: "badge-warning" },
    partial_outage: { label: "Partial Outage", className: "badge-danger" },
    major_outage: { label: "Major Outage", className: "badge-critical" },
    maintenance: { label: "Maintenance", className: "badge-info" },
};

export default function ServiceDetailPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = use(params);
    const { orgSlug, isLoading: orgLoading } = useOrg();
    const [service, setService] = useState<Service | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (orgLoading || !orgSlug) return;
        async function load() {
            try {
                const res = await fetch(`/api/proxy/orgs/${orgSlug}/services/${id}`, { credentials: "include" });
                if (res.ok) { setService(await res.json()); } else { setError("Service not found"); }
            } catch { setError("Failed to load service"); }
            finally { setIsLoading(false); }
        }
        load();
    }, [id, orgSlug, orgLoading]);

    if (isLoading || orgLoading) {
        return (<DashboardLayout><div className="page-loading"><Loader2 size={24} className="animate-spin" /><span>Loading...</span></div></DashboardLayout>);
    }

    if (error || !service) {
        return (<DashboardLayout><div className="page-container"><div className="page-error">{error || "Service not found"}</div><Link href={`/${orgSlug}/services`} className="btn btn-ghost"><ArrowLeft size={16} /> Back to Services</Link></div></DashboardLayout>);
    }

    const badge = STATUS_BADGES[service.status];

    return (
        <DashboardLayout>
            <div className="page-container">
                <div className="page-header">
                    <Link href={`/${orgSlug}/services`} className="btn btn-ghost"><ArrowLeft size={16} />Back to Services</Link>
                </div>
                <div className="detail-header">
                    <div>
                        <h1 className="detail-title">{service.name}</h1>
                        <span className="detail-slug">/{service.slug}</span>
                    </div>
                    <span className={`badge badge-lg ${badge.className}`}>{badge.label}</span>
                </div>
                {service.description && <p className="detail-description">{service.description}</p>}
                <div className="detail-grid">
                    <div className="detail-card">
                        <h3 className="detail-card-title">Details</h3>
                        <dl className="detail-list">
                            <div className="detail-item"><dt>Tier</dt><dd className="capitalize">{service.tier}</dd></div>
                            <div className="detail-item"><dt>Lifecycle</dt><dd className="capitalize">{service.lifecycle}</dd></div>
                            <div className="detail-item"><dt>Category</dt><dd>{service.category || "—"}</dd></div>
                            <div className="detail-item"><dt>Created</dt><dd>{new Date(service.created_at).toLocaleDateString()}</dd></div>
                        </dl>
                    </div>
                    <div className="detail-card">
                        <h3 className="detail-card-title">Support</h3>
                        <dl className="detail-list">
                            <div className="detail-item"><dt>Support Hours</dt><dd>{service.support_hours || "—"}</dd></div>
                            <div className="detail-item"><dt>SLA Tier</dt><dd>{service.sla_tier || "—"}</dd></div>
                            {service.documentation_url && (
                                <div className="detail-item"><dt>Documentation</dt><dd><a href={service.documentation_url} target="_blank" rel="noopener noreferrer" className="detail-link">View Docs <ExternalLink size={12} /></a></dd></div>
                            )}
                        </dl>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
