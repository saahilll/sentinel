import { NextResponse } from "next/server";
import { getSessionFromCookie, getBackendUrl, COOKIE_NAME } from "@/lib/server/session";

export async function POST() {
    try {
        const session = await getSessionFromCookie();

        if (session) {
            // Tell the backend to revoke the refresh token
            try {
                await fetch(getBackendUrl("/auth/logout"), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ refresh_token: session.refreshToken }),
                });
            } catch {
                // Ignore backend errors — we clear the cookie anyway
            }
        }

        const res = NextResponse.json({ success: true });
        res.cookies.delete(COOKIE_NAME);
        return res;
    } catch (error) {
        console.error("Logout error:", error);
        // Even on error, clear the cookie
        const res = NextResponse.json({ success: true });
        res.cookies.delete(COOKIE_NAME);
        return res;
    }
}
