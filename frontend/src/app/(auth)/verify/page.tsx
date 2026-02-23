"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, XCircle } from "lucide-react";

function BrandingPanel() {
    return (
        <div className="auth-branding">
            <div className="auth-branding-content">
                <p className="auth-branding-logo">Sentinel</p>
                <h2 className="auth-branding-headline">
                    AI-Native Incident<br />Management at Scale.
                </h2>
                <p className="auth-branding-sub">
                    Orchestrate response, automate triage, and maintain 99.99% uptime with the world&apos;s most advanced ITSM platform.
                </p>
                <div className="auth-branding-features">
                    <div className="auth-branding-feature"><span>Predictive Anomalies</span></div>
                    <div className="auth-branding-feature"><span>Automated Root Cause Analysis</span></div>
                    <div className="auth-branding-feature"><span>Global SLA Monitoring</span></div>
                </div>
            </div>
            <div className="auth-branding-footer">
                <a href="mailto:support@sentinel.ai" className="auth-footer-link">Support</a>
                <span className="auth-footer-sep" />
                <a href="#" className="auth-footer-link">Terms</a>
                <span className="auth-footer-sep" />
                <a href="#" className="auth-footer-link">Privacy</a>
            </div>
        </div>
    );
}

function VerifyContent() {
    const searchParams = useSearchParams();
    const token = searchParams.get("token");
    const flow = searchParams.get("flow");
    const [error, setError] = useState("");
    const [isVerifying, setIsVerifying] = useState(true);

    useEffect(() => {
        if (!token) {
            setError("Invalid or missing token.");
            setIsVerifying(false);
            return;
        }

        const verify = async () => {
            try {
                const response = await fetch("/api/auth/verify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token, flow }),
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.flow === "reset") {
                        window.location.href = "/auth/reset-password";
                    } else if (data.organizations && data.organizations.length > 1) {
                        window.location.href = "/select-org";
                    } else if (!data.organizations || data.organizations.length === 0) {
                        window.location.href = "/create-org";
                    } else {
                        window.location.href = `/${data.organizations[0].slug}/dashboard`;
                    }
                } else {
                    const data = await response.json();
                    setError(data.error || "Verification failed. The link may have expired.");
                }
            } catch {
                setError("Something went wrong. Please try again.");
            } finally {
                setIsVerifying(false);
            }
        };

        verify();
    }, [token, flow]);

    if (isVerifying) {
        return (
            <div className="auth-card">
                <Loader2 size={24} className="auth-spinner animate-spin" />
                <div className="auth-header">
                    <h1 className="auth-title">Verifying your link</h1>
                    <p className="auth-description">
                        {flow === "reset" ? "Please wait while we verify secure reset access." : "Please wait while we sign you in."}
                    </p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="auth-card">
                <div className="auth-icon-error">
                    <XCircle size={36} strokeWidth={1.5} />
                </div>
                <div className="auth-header">
                    <h1 className="auth-title">Verification failed</h1>
                    <p className="auth-description">{error}</p>
                </div>
                <a href="/login" className="auth-submit-btn auth-action">
                    Back to sign in
                </a>
            </div>
        );
    }

    return null;
}

function VerifyFallback() {
    return (
        <div className="auth-card">
            <Loader2 size={24} className="auth-spinner animate-spin" />
            <div className="auth-header">
                <h1 className="auth-title">Loading</h1>
            </div>
        </div>
    );
}

export default function VerifyPage() {
    return (
        <div className="auth-split">
            <BrandingPanel />
            <div className="auth-panel">
                <div className="auth-panel-inner">
                    <Suspense fallback={<VerifyFallback />}>
                        <VerifyContent />
                    </Suspense>
                </div>
            </div>
        </div>
    );
}
