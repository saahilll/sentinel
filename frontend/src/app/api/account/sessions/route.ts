import { NextRequest } from "next/server";
import { authenticatedProxy } from "@/lib/server/proxy";

export async function GET(request: NextRequest) {
    return authenticatedProxy(request, {
        method: "GET",
        path: "/auth/sessions",
    });
}
