"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, LogOut } from "lucide-react";
import Link from "next/link";
import Navbar from "@/components/dashboard/Navbar";

export default function CreateOrgPage() {
    const router = useRouter();
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError("");

        try {
            const res = await fetch("/api/user/organizations", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    name,
                    description: description || null,
                }),
            });

            if (res.ok) {
                const data = await res.json();
                window.location.href = `/${data.slug}/dashboard`;
            } else {
                const data = await res.json().catch(() => ({}));
                setError(data.detail || data.error || "Failed to create organization");
            }
        } catch {
            setError("Something went wrong. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleLogout = async () => {
        await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "include",
        });
        router.push("/login");
    };

    return (
        <div className="standalone-layout">
            <header className="standalone-topbar">
                <div className="standalone-topbar-left">
                    <Link href="/" className="standalone-logo">
                        <span className="standalone-logo-text">Sentinel</span>
                    </Link>
                </div>
                <button
                    onClick={handleLogout}
                    className="btn btn-ghost"
                    style={{ gap: "6px" }}
                >
                    <LogOut size={14} />
                    Sign out
                </button>
            </header>

            <div className="standalone-content">
                <div className="create-app-page">
                    <h1 className="create-app-page-title">Create Organization</h1>
                    <p className="create-app-page-description">
                        An organization is your workspace in Sentinel. Incidents, services, and team members are managed under it.
                    </p>

                    {error && <div className="create-app-error">{error}</div>}

                    <form onSubmit={handleSubmit} className="create-app-form">
                        <div className="create-app-field">
                            <label className="create-app-label">Organization Name</label>
                            <input
                                type="text"
                                className="create-app-input"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="e.g. Acme Corp"
                                required
                                maxLength={255}
                                autoFocus
                                disabled={isSubmitting}
                            />
                        </div>

                        <div className="create-app-field">
                            <label className="create-app-label">
                                Description <span className="create-app-optional">(optional)</span>
                            </label>
                            <textarea
                                className="create-app-textarea"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="A short description of your organization"
                                rows={3}
                                maxLength={500}
                                disabled={isSubmitting}
                            />
                        </div>

                        <div className="create-app-actions">
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={isSubmitting || !name.trim()}
                            >
                                {isSubmitting ? (
                                    <Loader2 size={16} className="animate-spin" />
                                ) : (
                                    "Create Organization"
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
