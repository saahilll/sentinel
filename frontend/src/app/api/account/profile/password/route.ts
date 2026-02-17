import { NextRequest } from "next/server";
import { authenticatedProxy } from "@/lib/server/proxy";

export async function POST(request: NextRequest) {
    const body = await request.text();
    return authenticatedProxy(request, {
        method: "POST",
        path: "/auth/profile/password",
        body,
    });
}
