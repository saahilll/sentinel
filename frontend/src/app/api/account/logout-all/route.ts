import { NextRequest } from "next/server";
import { authenticatedProxy } from "@/lib/server/proxy";

export async function POST(request: NextRequest) {
    return authenticatedProxy(request, {
        method: "POST",
        path: "/auth/logout-all",
    });
}
