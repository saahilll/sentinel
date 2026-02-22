import { NextRequest, NextResponse } from "next/server";
import { buildSessionCookie, getBackendUrl, type SessionData } from "@/lib/server/session";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const response = await fetch(getBackendUrl("/auth/verify-otp"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
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

        const res = NextResponse.json({ success: true, organizations: data.organizations });
        res.cookies.set(cookie);

        return res;
    } catch (error) {
        console.error("OTP verify error:", error);
        return NextResponse.json(
            { error: "Verification failed" },
            { status: 500 },
        );
    }
}
