import { NextResponse } from "next/server";
import { getSessionFromCookie, refreshSession, buildSessionCookie, COOKIE_NAME } from "@/lib/server/session";

export async function POST() {
    try {
        const session = await getSessionFromCookie();
        if (!session) {
            return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
        }

        const newSession = await refreshSession(session);
        if (!newSession) {
            const res = NextResponse.json({ error: "Session expired" }, { status: 401 });
            res.cookies.delete(COOKIE_NAME);
            return res;
        }

        const res = NextResponse.json({ success: true });
        res.cookies.set(buildSessionCookie(newSession));
        return res;
    } catch (error) {
        console.error("Refresh error:", error);
        return NextResponse.json(
            { error: "Refresh failed" },
            { status: 500 },
        );
    }
}
