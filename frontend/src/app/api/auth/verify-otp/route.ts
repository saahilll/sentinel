import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "@/lib/server/session";

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

        // The session helper or caller will handle setting the cookie since we return tokens
        return NextResponse.json(data);
    } catch (error) {
        console.error("OTP verify error:", error);
        return NextResponse.json(
            { error: "Verification failed" },
            { status: 500 },
        );
    }
}
