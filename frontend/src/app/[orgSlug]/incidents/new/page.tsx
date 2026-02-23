"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";
import type { IncidentImpact, IncidentUrgency } from "@/types/incident";

export default function CreateIncidentPage() {
    const router = useRouter();
    const { orgSlug } = useOrg();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState("");

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [impact, setImpact] = useState<IncidentImpact>("medium");
    const [urgency, setUrgency] = useState<IncidentUrgency>("medium");
    const [category, setCategory] = useState("");
    const [subcategory, setSubcategory] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!orgSlug) return;
        setIsSubmitting(true);
        setError("");

        try {
            const res = await fetch(`/api/proxy/orgs/${orgSlug}/incidents`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    description: description || null,
                    impact,
                    urgency,
                    category: category || null,
                    subcategory: subcategory || null,
                    source: "portal",
                }),
            });

            if (res.ok) {
                router.push(`/${orgSlug}/incidents`);
            } else {
                const data = await res.json().catch(() => ({}));
                setError(data.detail || "Failed to create incident");
            }
        } catch {
            setError("Failed to create incident");
        } finally {
            setIsSubmitting(false);
        }
    };

    const priorityMatrix: Record<string, string> = {
        "high-high": "P1 — Critical", "high-medium": "P2 — High", "high-low": "P3 — Medium",
        "medium-high": "P2 — High", "medium-medium": "P3 — Medium", "medium-low": "P4 — Low",
        "low-high": "P3 — Medium", "low-medium": "P4 — Low", "low-low": "P4 — Low",
    };
    const computedPriority = priorityMatrix[`${impact}-${urgency}`] || "P3";

    return (
        <DashboardLayout>
            <div className="page-container page-container-narrow">
                <div className="page-header">
                    <Link href={`/${orgSlug}/incidents`} className="btn btn-ghost"><ArrowLeft size={16} />Back to Incidents</Link>
                </div>
                <div className="form-card">
                    <h1 className="form-title">Report Incident</h1>
                    <p className="form-subtitle">Create a new incident report</p>
                    {error && <div className="form-error">{error}</div>}
                    <form onSubmit={handleSubmit} className="form-stack">
                        <div className="form-group">
                            <label className="form-label">Title *</label>
                            <input className="form-input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Brief summary of the incident" required minLength={1} maxLength={500} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <textarea className="form-textarea" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Detailed description of the issue" rows={4} />
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Impact</label>
                                <select className="form-select" value={impact} onChange={(e) => setImpact(e.target.value as IncidentImpact)}>
                                    <option value="high">High — Widespread</option>
                                    <option value="medium">Medium — Limited</option>
                                    <option value="low">Low — Minimal</option>
                                </select>
                                <span className="form-hint">How many users/services are affected?</span>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Urgency</label>
                                <select className="form-select" value={urgency} onChange={(e) => setUrgency(e.target.value as IncidentUrgency)}>
                                    <option value="high">High — Immediate</option>
                                    <option value="medium">Medium — Soon</option>
                                    <option value="low">Low — Can wait</option>
                                </select>
                                <span className="form-hint">How quickly does this need to be resolved?</span>
                            </div>
                        </div>
                        <div className="form-priority-preview">Computed Priority: <strong>{computedPriority}</strong></div>
                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Category</label>
                                <input className="form-input" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. Network, Application" maxLength={100} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Subcategory</label>
                                <input className="form-input" value={subcategory} onChange={(e) => setSubcategory(e.target.value)} placeholder="e.g. DNS, Login" maxLength={100} />
                            </div>
                        </div>
                        <div className="form-actions">
                            <Link href={`/${orgSlug}/incidents`} className="btn btn-ghost">Cancel</Link>
                            <button type="submit" className="btn btn-primary" disabled={isSubmitting || !title.trim()}>
                                {isSubmitting && <Loader2 size={16} className="animate-spin" />}
                                Create Incident
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </DashboardLayout>
    );
}
