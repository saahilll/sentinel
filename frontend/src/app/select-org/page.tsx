"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, ArrowRight, Loader2, LogOut } from "lucide-react";

interface Organization {
    id: string;
    name: string;
    slug: string;
    role: string;
}

export default function SelectOrgPage() {
    const router = useRouter();
    const [orgs, setOrgs] = useState<Organization[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSelecting, setIsSelecting] = useState<string | null>(null);

    useEffect(() => {
        // Fetch session data which now contains the active organizations
        // Actually, we need an endpoint to get the user's organizations
        // But for now, let's hit /api/auth/me which we can update to return orgs 
        // OR we can hit a new endpoint. 
        // Wait, the easiest way is to read them from a dedicated endpoint.

        const fetchOrgs = async () => {
            try {
                // We'll add this endpoint next if it doesn't exist
                const res = await fetch("/api/user/organizations", { credentials: "include" });
                if (!res.ok) {
                    if (res.status === 401) router.push("/login");
                    throw new Error("Failed to fetch organizations");
                }
                const data = await res.json();

                if (!data.organizations || data.organizations.length === 0) {
                    router.push("/create-org");
                    return;
                }

                if (data.organizations.length === 1) {
                    // Auto redirect if only one
                    router.push(`/${data.organizations[0].slug}/dashboard`);
                    return;
                }

                setOrgs(data.organizations || []);
            } catch (err) {
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchOrgs();
    }, [router]);

    const handleSelect = async (orgId: string, slug: string) => {
        setIsSelecting(orgId);
        try {
            // Here we would typically set the active org in a cookie or context
            // For now, we just redirect to the dashboard which will use the default or selected org
            // In a real multi-tenant app, the dashboard URL might be /apps/[slug] or similar
            // Looking at the app router, there is apps/[slug]/page.tsx

            router.push(`/${slug}/dashboard`);
        } catch (err) {
            console.error(err);
            setIsSelecting(null);
        }
    };

    const handleLogout = async () => {
        await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "include",
        });
        router.push("/login");
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Loader2 size={32} className="animate-spin text-zinc-500" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white flex flex-col pt-20 px-4">
            <div className="max-w-md w-full mx-auto">
                <div className="mb-8 text-center">
                    <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-900 border border-zinc-800 mb-4">
                        <Building2 size={24} className="text-zinc-400" />
                    </div>
                    <h1 className="text-2xl font-bold mb-2">Select Organization</h1>
                    <p className="text-zinc-400">Choose an organization to continue</p>
                </div>

                <div className="space-y-3 mb-8">
                    {orgs.length > 0 ? (
                        orgs.map((org) => (
                            <button
                                key={org.id}
                                onClick={() => handleSelect(org.id, org.slug)}
                                disabled={isSelecting !== null}
                                className="w-full text-left p-4 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800/80 transition-all flex items-center justify-between group"
                            >
                                <div>
                                    <div className="font-medium text-lg mb-1">{org.name}</div>
                                    <div className="text-sm text-zinc-500 capitalize">{org.role} Role</div>
                                </div>
                                {isSelecting === org.id ? (
                                    <Loader2 size={18} className="animate-spin text-zinc-400" />
                                ) : (
                                    <ArrowRight size={18} className="text-zinc-600 group-hover:text-zinc-300 transition-colors" />
                                )}
                            </button>
                        ))
                    ) : (
                        <div className="text-center p-8 bg-zinc-900 border border-zinc-800 rounded-xl">
                            <p className="text-zinc-400">You don&apos;t belong to any organizations yet.</p>
                        </div>
                    )}
                </div>

                <div className="text-center">
                    <button
                        onClick={handleLogout}
                        className="text-sm text-zinc-500 hover:text-white transition-colors inline-flex items-center"
                    >
                        <LogOut size={14} className="mr-2" />
                        Sign out instead
                    </button>
                </div>
            </div>
        </div>
    );
}
