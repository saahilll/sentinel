export type IncidentStatus = "open" | "acknowledged" | "investigating" | "resolved" | "closed";
export type IncidentImpact = "high" | "medium" | "low";
export type IncidentUrgency = "high" | "medium" | "low";
export type IncidentPriority = "P1" | "P2" | "P3" | "P4";
export type IncidentSource = "portal" | "email" | "monitoring" | "api" | "phone";

export interface IncidentAttachment {
    id: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    uploaded_by: string | null;
    created_at: string;
}

export interface Incident {
    id: string;
    organization_id: string;
    incident_number: string;
    title: string;
    description: string | null;
    status: IncidentStatus;
    impact: IncidentImpact;
    urgency: IncidentUrgency;
    priority: IncidentPriority;
    category: string | null;
    subcategory: string | null;
    source: IncidentSource;
    service_id: string | null;
    assigned_to: string | null;
    reported_by: string;
    diagnosis: string | null;
    solution: string | null;
    resolution_notes: string | null;
    sla_due_at: string | null;
    acknowledged_at: string | null;
    resolved_at: string | null;
    closed_at: string | null;
    created_at: string;
    updated_at: string;
    attachments: IncidentAttachment[];
}

export interface IncidentListItem {
    id: string;
    incident_number: string;
    title: string;
    status: IncidentStatus;
    impact: IncidentImpact;
    urgency: IncidentUrgency;
    priority: IncidentPriority;
    category: string | null;
    source: IncidentSource;
    service_id: string | null;
    assigned_to: string | null;
    reported_by: string;
    created_at: string;
}
