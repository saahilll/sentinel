import { NextRequest } from "next/server";
import { authenticatedProxy } from "@/lib/server/proxy";

export async function DELETE(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> },
) {
    const { id } = await params;
    return authenticatedProxy(request, {
        method: "DELETE",
        path: `/auth/sessions/${id}`,
    });
}
