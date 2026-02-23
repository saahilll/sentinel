"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Plus, Loader2, AlertTriangle, RefreshCw } from "lucide-react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";
import type { IncidentListItem, IncidentStatus, IncidentPriority } from "@/types/incident";

const STATUS_BADGES: Record<IncidentStatus, { label: string; className: string }> = {
    open: { label: "Open", className: "badge-danger" },
    acknowledged: { label: "Acknowledged", className: "badge-warning" },
    investigating: { label: "Investigating", className: "badge-info" },
    resolved: { label: "Resolved", className: "badge-success" },
    closed: { label: "Closed", className: "badge-muted" },
};

const PRIORITY_BADGES: Record<IncidentPriority, { label: string; className: string }> = {
    P1: { label: "P1", className: "badge-critical" },
    P2: { label: "P2", className: "badge-danger" },
    P3: { label: "P3", className: "badge-warning" },
    P4: { label: "P4", className: "badge-muted" },
};

export default function IncidentsPage() {
    const router = useRouter();
    const { orgSlug, isLoading: orgLoading } = useOrg();
    const [incidents, setIncidents] = useState<IncidentListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");
    const [statusFilter, setStatusFilter] = useState<string>("");
    const [priorityFilter, setPriorityFilter] = useState<string>("");

    const fetchIncidents = async () => {
        if (!orgSlug) return;
        setIsLoading(true);
        try {
            const params = new URLSearchParams();
            if (statusFilter) params.set("status", statusFilter);
            if (priorityFilter) params.set("priority", priorityFilter);
            const qs = params.toString() ? `?${params.toString()}` : "";
            const res = await fetch(`/api/proxy/orgs/${orgSlug}/incidents${qs}`, { credentials: "include" });
            if (res.ok) { setIncidents(await res.json()); } else { setError("Failed to load incidents"); }
        } catch { setError("Failed to load incidents"); }
        finally { setIsLoading(false); }
    };

    useEffect(() => {
        if (!orgLoading && orgSlug) fetchIncidents();
    }, [statusFilter, priorityFilter, orgSlug, orgLoading]);

    return (
        <DashboardLayout>
            <div className="page-container">
                <div className="page-header">
                    <div>
                        <h1 className="page-title">Incidents</h1>
                        <p className="page-subtitle">Track and manage IT incidents</p>
                    </div>
                    <div className="page-actions">
                        <button className="btn btn-ghost" onClick={fetchIncidents} title="Refresh"><RefreshCw size={16} /></button>
                        <Link href={`/${orgSlug}/incidents/new`} className="btn btn-primary"><Plus size={16} />Report Incident</Link>
                    </div>
                </div>

                <div className="filter-bar">
                    <select className="form-select form-select-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                        <option value="">All Statuses</option>
                        <option value="open">Open</option>
                        <option value="acknowledged">Acknowledged</option>
                        <option value="investigating">Investigating</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                    </select>
                    <select className="form-select form-select-sm" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
                        <option value="">All Priorities</option>
                        <option value="P1">P1 — Critical</option>
                        <option value="P2">P2 — High</option>
                        <option value="P3">P3 — Medium</option>
                        <option value="P4">P4 — Low</option>
                    </select>
                </div>

                {isLoading || orgLoading ? (
                    <div className="page-loading"><Loader2 size={24} className="animate-spin" /><span>Loading incidents...</span></div>
                ) : error ? (
                    <div className="page-error">{error}</div>
                ) : incidents.length === 0 ? (
                    <div className="page-empty">
                        <AlertTriangle size={48} strokeWidth={1} />
                        <h2>No incidents found</h2>
                        <p>{statusFilter || priorityFilter ? "No incidents match your filters." : "No incidents have been reported yet."}</p>
                        {!statusFilter && !priorityFilter && (
                            <Link href={`/${orgSlug}/incidents/new`} className="btn btn-primary"><Plus size={16} />Report Incident</Link>
                        )}
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr><th>ID</th><th>Title</th><th>Status</th><th>Priority</th><th>Category</th><th>Source</th><th>Reported</th></tr>
                            </thead>
                            <tbody>
                                {incidents.map((inc) => {
                                    const statusBadge = STATUS_BADGES[inc.status];
                                    const priorityBadge = PRIORITY_BADGES[inc.priority];
                                    return (
                                        <tr key={inc.id} className="table-row-clickable" onClick={() => router.push(`/${orgSlug}/incidents/${inc.id}`)}>
                                            <td className="table-cell-mono">{inc.incident_number}</td>
                                            <td className="table-cell-primary">{inc.title}</td>
                                            <td><span className={`badge ${statusBadge.className}`}>{statusBadge.label}</span></td>
                                            <td><span className={`badge ${priorityBadge.className}`}>{priorityBadge.label}</span></td>
                                            <td>{inc.category || "—"}</td>
                                            <td className="capitalize">{inc.source}</td>
                                            <td className="table-cell-muted">{new Date(inc.created_at).toLocaleDateString()}</td>
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
