import { NextRequest } from "next/server";
import { authenticatedProxy } from "@/lib/server/proxy";

export async function GET(request: NextRequest) {
    return authenticatedProxy(request, {
        method: "GET",
        path: "/auth/profile",
    });
}

export async function PATCH(request: NextRequest) {
    const body = await request.text();
    return authenticatedProxy(request, {
        method: "PATCH",
        path: "/auth/profile",
        body,
    });
}

export async function DELETE(request: NextRequest) {
    return authenticatedProxy(request, {
        method: "DELETE",
        path: "/auth/profile",
    });
}
