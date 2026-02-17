import { NextResponse } from "next/server";
import { getSessionFromCookie, refreshSession, buildSessionCookie, getBackendUrl } from "@/lib/server/session";

export async function GET() {
    try {
        const session = await getSessionFromCookie();
        if (!session) {
            return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
        }

        // Try to get user info with current access token
        let response = await fetch(getBackendUrl("/auth/me"), {
            headers: { Authorization: `Bearer ${session.accessToken}` },
        });

        // If access token expired, try refreshing
        if (response.status === 401) {
            const newSession = await refreshSession(session);
            if (!newSession) {
                // Refresh also failed — clear cookie
                const res = NextResponse.json({ error: "Session expired" }, { status: 401 });
                res.cookies.delete("sentinel_session");
                return res;
            }

            // Retry with new access token
            response = await fetch(getBackendUrl("/auth/me"), {
                headers: { Authorization: `Bearer ${newSession.accessToken}` },
            });

            if (!response.ok) {
                const res = NextResponse.json({ error: "Session expired" }, { status: 401 });
                res.cookies.delete("sentinel_session");
                return res;
            }

            // Update cookie with new tokens
            const data = await response.json();
            const res = NextResponse.json(data);
            res.cookies.set(buildSessionCookie(newSession));
            return res;
        }

        if (!response.ok) {
            return NextResponse.json(
                { error: "Failed to get user info" },
                { status: response.status },
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Me error:", error);
        return NextResponse.json(
            { error: "Failed to get user info" },
            { status: 500 },
        );
    }
}
