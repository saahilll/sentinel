import { NextRequest, NextResponse } from "next/server";
import {
    getSessionFromCookie,
    refreshSession,
    buildSessionCookie,
    COOKIE_NAME,
} from "@/lib/server/session";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

/**
 * Catch-all API proxy.
 *
 * All requests to /api/proxy/[...path] are forwarded to the FastAPI backend
 * with the access token from the encrypted httpOnly cookie.
 *
 * If the token is expired (401 from backend), the proxy silently refreshes
 * and retries once before returning 401 to the client.
 */
async function handler(
    request: NextRequest,
    { params }: { params: Promise<{ path: string[] }> },
) {
    const { path } = await params;
    const targetPath = path.join("/");
    const url = new URL(request.url);
    const queryString = url.search;
    const backendUrl = `${BACKEND_URL}/api/${targetPath}${queryString}`;

    // Get session
    const session = await getSessionFromCookie();
    if (!session) {
        return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    // Build headers
    const headers: Record<string, string> = {
        Authorization: `Bearer ${session.accessToken}`,
    };

    // Forward content-type if present
    const contentType = request.headers.get("content-type");
    if (contentType) {
        headers["Content-Type"] = contentType;
    }

    // Forward the request body for non-GET requests
    let body: string | null = null;
    if (request.method !== "GET" && request.method !== "HEAD") {
        body = await request.text();
    }

    // Make the request
    let response = await fetch(backendUrl, {
        method: request.method,
        headers,
        body,
    });

    // If 401, try refresh and retry
    if (response.status === 401) {
        const newSession = await refreshSession(session);
        if (!newSession) {
            const res = NextResponse.json({ error: "Session expired" }, { status: 401 });
            res.cookies.delete(COOKIE_NAME);
            return res;
        }

        // Retry with new token
        headers.Authorization = `Bearer ${newSession.accessToken}`;
        response = await fetch(backendUrl, {
            method: request.method,
            headers,
            body,
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({ detail: "Request failed" }));
            return NextResponse.json(data, { status: response.status });
        }

        // Return data with updated cookie
        const data = await response.json().catch(() => null);
        const res = data !== null
            ? NextResponse.json(data, { status: response.status })
            : new NextResponse(null, { status: response.status });
        res.cookies.set(buildSessionCookie(newSession));
        return res;
    }

    // Forward the response
    if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: "Request failed" }));
        return NextResponse.json(data, { status: response.status });
    }

    const data = await response.json().catch(() => null);
    if (data !== null) {
        return NextResponse.json(data, { status: response.status });
    }
    return new NextResponse(null, { status: response.status });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
