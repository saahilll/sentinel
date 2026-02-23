"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { ArrowLeft, Loader2, Paperclip } from "lucide-react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";
import type { Incident, IncidentStatus, IncidentPriority } from "@/types/incident";

const STATUS_BADGES: Record<IncidentStatus, { label: string; className: string }> = {
    open: { label: "Open", className: "badge-danger" },
    acknowledged: { label: "Acknowledged", className: "badge-warning" },
    investigating: { label: "Investigating", className: "badge-info" },
    resolved: { label: "Resolved", className: "badge-success" },
    closed: { label: "Closed", className: "badge-muted" },
};

const PRIORITY_BADGES: Record<IncidentPriority, { label: string; className: string }> = {
    P1: { label: "P1 — Critical", className: "badge-critical" },
    P2: { label: "P2 — High", className: "badge-danger" },
    P3: { label: "P3 — Medium", className: "badge-warning" },
    P4: { label: "P4 — Low", className: "badge-muted" },
};

export default function IncidentDetailPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = use(params);
    const { orgSlug, isLoading: orgLoading } = useOrg();
    const [incident, setIncident] = useState<Incident | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (orgLoading || !orgSlug) return;
        async function load() {
            try {
                const res = await fetch(`/api/proxy/orgs/${orgSlug}/incidents/${id}`, { credentials: "include" });
                if (res.ok) { setIncident(await res.json()); } else { setError("Incident not found"); }
            } catch { setError("Failed to load incident"); }
            finally { setIsLoading(false); }
        }
        load();
    }, [id, orgSlug, orgLoading]);

    if (isLoading || orgLoading) {
        return (<DashboardLayout><div className="page-loading"><Loader2 size={24} className="animate-spin" /><span>Loading...</span></div></DashboardLayout>);
    }

    if (error || !incident) {
        return (<DashboardLayout><div className="page-container"><div className="page-error">{error || "Incident not found"}</div><Link href={`/${orgSlug}/incidents`} className="btn btn-ghost"><ArrowLeft size={16} /> Back to Incidents</Link></div></DashboardLayout>);
    }

    const statusBadge = STATUS_BADGES[incident.status];
    const priorityBadge = PRIORITY_BADGES[incident.priority];

    return (
        <DashboardLayout>
            <div className="page-container">
                <div className="page-header">
                    <Link href={`/${orgSlug}/incidents`} className="btn btn-ghost"><ArrowLeft size={16} />Back to Incidents</Link>
                </div>
                <div className="detail-header">
                    <div>
                        <span className="detail-slug">{incident.incident_number}</span>
                        <h1 className="detail-title">{incident.title}</h1>
                    </div>
                    <div className="detail-badges">
                        <span className={`badge badge-lg ${statusBadge.className}`}>{statusBadge.label}</span>
                        <span className={`badge badge-lg ${priorityBadge.className}`}>{priorityBadge.label}</span>
                    </div>
                </div>
                {incident.description && <p className="detail-description">{incident.description}</p>}
                <div className="detail-grid">
                    <div className="detail-card">
                        <h3 className="detail-card-title">Classification</h3>
                        <dl className="detail-list">
                            <div className="detail-item"><dt>Impact</dt><dd className="capitalize">{incident.impact}</dd></div>
                            <div className="detail-item"><dt>Urgency</dt><dd className="capitalize">{incident.urgency}</dd></div>
                            <div className="detail-item"><dt>Category</dt><dd>{incident.category || "—"}</dd></div>
                            <div className="detail-item"><dt>Subcategory</dt><dd>{incident.subcategory || "—"}</dd></div>
                            <div className="detail-item"><dt>Source</dt><dd className="capitalize">{incident.source}</dd></div>
                        </dl>
                    </div>
                    <div className="detail-card">
                        <h3 className="detail-card-title">Timeline</h3>
                        <dl className="detail-list">
                            <div className="detail-item"><dt>Reported</dt><dd>{new Date(incident.created_at).toLocaleString()}</dd></div>
                            {incident.acknowledged_at && <div className="detail-item"><dt>Acknowledged</dt><dd>{new Date(incident.acknowledged_at).toLocaleString()}</dd></div>}
                            {incident.resolved_at && <div className="detail-item"><dt>Resolved</dt><dd>{new Date(incident.resolved_at).toLocaleString()}</dd></div>}
                            {incident.closed_at && <div className="detail-item"><dt>Closed</dt><dd>{new Date(incident.closed_at).toLocaleString()}</dd></div>}
                            {incident.sla_due_at && <div className="detail-item"><dt>SLA Due</dt><dd>{new Date(incident.sla_due_at).toLocaleString()}</dd></div>}
                        </dl>
                    </div>
                </div>
                {(incident.diagnosis || incident.solution || incident.resolution_notes) && (
                    <div className="detail-card" style={{ marginTop: "1.5rem" }}>
                        <h3 className="detail-card-title">Resolution</h3>
                        <dl className="detail-list">
                            {incident.diagnosis && <div className="detail-item detail-item-full"><dt>Diagnosis</dt><dd className="detail-text-block">{incident.diagnosis}</dd></div>}
                            {incident.solution && <div className="detail-item detail-item-full"><dt>Solution</dt><dd className="detail-text-block">{incident.solution}</dd></div>}
                            {incident.resolution_notes && <div className="detail-item detail-item-full"><dt>Resolution Notes</dt><dd className="detail-text-block">{incident.resolution_notes}</dd></div>}
                        </dl>
                    </div>
                )}
                {incident.attachments && incident.attachments.length > 0 && (
                    <div className="detail-card" style={{ marginTop: "1.5rem" }}>
                        <h3 className="detail-card-title"><Paperclip size={16} /> Attachments ({incident.attachments.length})</h3>
                        <ul className="attachment-list">
                            {incident.attachments.map((att) => (
                                <li key={att.id} className="attachment-item">
                                    <span className="attachment-name">{att.filename}</span>
                                    <span className="attachment-size">{(att.size_bytes / 1024).toFixed(1)} KB</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
