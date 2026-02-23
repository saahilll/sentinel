export type ServiceStatus = "operational" | "degraded" | "partial_outage" | "major_outage" | "maintenance";
export type ServiceTier = "critical" | "high" | "medium" | "low";
export type ServiceLifecycle = "pipeline" | "active" | "retired";

export interface Service {
    id: string;
    organization_id: string;
    name: string;
    slug: string;
    description: string | null;
    status: ServiceStatus;
    tier: ServiceTier;
    lifecycle: ServiceLifecycle;
    category: string | null;
    owner_id: string | null;
    support_hours: string | null;
    sla_tier: string | null;
    documentation_url: string | null;
    created_at: string;
    updated_at: string;
}

export interface ServiceListItem {
    id: string;
    name: string;
    slug: string;
    status: ServiceStatus;
    tier: ServiceTier;
    lifecycle: ServiceLifecycle;
    category: string | null;
    owner_id: string | null;
    created_at: string;
}
