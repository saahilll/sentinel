"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";

interface OrgInfo {
    id: string;
    name: string;
    slug: string;
    role: string;
}

interface OrgContextType {
    org: OrgInfo | null;
    orgSlug: string;
    isLoading: boolean;
}

const OrgContext = createContext<OrgContextType>({
    org: null,
    orgSlug: "",
    isLoading: true,
});

export function OrgProvider({ children }: { children: React.ReactNode }) {
    const params = useParams();
    const slugFromUrl = params.orgSlug as string;
    const [org, setOrg] = useState<OrgInfo | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchOrg = useCallback(async () => {
        if (!slugFromUrl) {
            setIsLoading(false);
            return;
        }

        try {
            const res = await fetch("/api/user/organizations", { credentials: "include" });
            if (!res.ok) {
                if (res.status === 401) {
                    window.location.href = "/login";
                    return;
                }
                setIsLoading(false);
                return;
            }
            const data = await res.json();
            const orgs: OrgInfo[] = Array.isArray(data) ? data : (data.organizations || []);

            if (orgs.length === 0) {
                window.location.href = "/create-org";
                return;
            }

            // Find the org matching the URL slug
            const matched = orgs.find((o) => o.slug === slugFromUrl);
            if (matched) {
                setOrg(matched);
            } else {
                // Slug doesn't match any user org — redirect to their first org
                window.location.href = `/${orgs[0].slug}/dashboard`;
                return;
            }
        } catch {
            // ignore
        } finally {
            setIsLoading(false);
        }
    }, [slugFromUrl]);

    useEffect(() => {
        fetchOrg();
    }, [fetchOrg]);

    return (
        <OrgContext.Provider value={{ org, orgSlug: slugFromUrl, isLoading }}>
            {children}
        </OrgContext.Provider>
    );
}

export function useOrg() {
    return useContext(OrgContext);
}
