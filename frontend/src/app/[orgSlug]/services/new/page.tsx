"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useOrg } from "@/components/providers/OrgProvider";
import type { ServiceTier, ServiceLifecycle } from "@/types/service";

export default function CreateServicePage() {
    const router = useRouter();
    const { orgSlug } = useOrg();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState("");

    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [tier, setTier] = useState<ServiceTier>("medium");
    const [lifecycle, setLifecycle] = useState<ServiceLifecycle>("active");
    const [category, setCategory] = useState("");
    const [supportHours, setSupportHours] = useState("");
    const [slaTier, setSlaTier] = useState("");
    const [documentationUrl, setDocumentationUrl] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!orgSlug) return;
        setIsSubmitting(true);
        setError("");

        try {
            const res = await fetch(`/api/proxy/orgs/${orgSlug}/services`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name,
                    description: description || null,
                    tier,
                    lifecycle,
                    category: category || null,
                    support_hours: supportHours || null,
                    sla_tier: slaTier || null,
                    documentation_url: documentationUrl || null,
                }),
            });

            if (res.ok) {
                router.push(`/${orgSlug}/services`);
            } else {
                const data = await res.json().catch(() => ({}));
                setError(data.detail || "Failed to create service");
            }
        } catch {
            setError("Failed to create service");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="page-container page-container-narrow">
                <div className="page-header">
                    <Link href={`/${orgSlug}/services`} className="btn btn-ghost">
                        <ArrowLeft size={16} />
                        Back to Services
                    </Link>
                </div>

                <div className="form-card">
                    <h1 className="form-title">Add Service</h1>
                    <p className="form-subtitle">Add a new service to the catalog</p>

                    {error && <div className="form-error">{error}</div>}

                    <form onSubmit={handleSubmit} className="form-stack">
                        <div className="form-group">
                            <label className="form-label">Service Name *</label>
                            <input className="form-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Payment Gateway" required minLength={1} maxLength={255} />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <textarea className="form-textarea" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Brief description of the service" rows={3} />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Tier</label>
                                <select className="form-select" value={tier} onChange={(e) => setTier(e.target.value as ServiceTier)}>
                                    <option value="critical">Critical</option>
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Lifecycle</label>
                                <select className="form-select" value={lifecycle} onChange={(e) => setLifecycle(e.target.value as ServiceLifecycle)}>
                                    <option value="pipeline">Pipeline</option>
                                    <option value="active">Active</option>
                                    <option value="retired">Retired</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Category</label>
                            <input className="form-input" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. Infrastructure, Business Application" maxLength={100} />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Support Hours</label>
                                <input className="form-input" value={supportHours} onChange={(e) => setSupportHours(e.target.value)} placeholder="e.g. 24/7, Business Hours" />
                            </div>
                            <div className="form-group">
                                <label className="form-label">SLA Tier</label>
                                <input className="form-input" value={slaTier} onChange={(e) => setSlaTier(e.target.value)} placeholder="e.g. Gold, Silver, Bronze" />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Documentation URL</label>
                            <input className="form-input" value={documentationUrl} onChange={(e) => setDocumentationUrl(e.target.value)} placeholder="https://wiki.example.com/service-docs" type="url" />
                        </div>

                        <div className="form-actions">
                            <Link href={`/${orgSlug}/services`} className="btn btn-ghost">Cancel</Link>
                            <button type="submit" className="btn btn-primary" disabled={isSubmitting || !name.trim()}>
                                {isSubmitting && <Loader2 size={16} className="animate-spin" />}
                                Create Service
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </DashboardLayout>
    );
}
