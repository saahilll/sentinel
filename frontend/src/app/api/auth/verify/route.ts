import { NextRequest, NextResponse } from "next/server";
import { buildSessionCookie, getBackendUrl, type SessionData } from "@/lib/server/session";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const userAgent = request.headers.get("user-agent") || "";
        const clientIp = request.headers.get("x-forwarded-for")?.split(",")[0].trim()
            || request.headers.get("x-real-ip")
            || "unknown";

        const response = await fetch(getBackendUrl("/auth/verify"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "User-Agent": userAgent,
                "X-Forwarded-For": clientIp,
            },
            body: JSON.stringify({
                token: body.token,
                device_info: userAgent.substring(0, 255),
                remember_me: body.remember_me ?? true,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            return NextResponse.json(
                { error: data.detail || "Verification failed" },
                { status: response.status },
            );
        }

        // Decode JWT to get user info (no verification needed — FastAPI already verified)
        const payload = JSON.parse(
            Buffer.from(data.access_token.split(".")[1], "base64url").toString(),
        );

        const sessionData: SessionData = {
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
            user: {
                id: payload.sub,
                email: payload.email,
            },
        };

        const rememberMe = body.remember_me ?? true;
        const cookie = buildSessionCookie(sessionData, rememberMe);

        const res = NextResponse.json({ success: true, flow: body.flow || null });
        res.cookies.set(cookie);

        return res;
    } catch (error) {
        console.error("Verify error:", error);
        return NextResponse.json(
            { error: "Verification failed" },
            { status: 500 },
        );
    }
}
