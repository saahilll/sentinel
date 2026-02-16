import { DashboardLayout } from "@/components/dashboard";
// import { redirect } from "next/navigation";
// import { getSession } from "@/lib/session";

export default async function AppLayout({
    children,
    params,
}: {
    children: React.ReactNode;
    params: Promise<{ slug: string }>;
}) {
    // Client-side auth check handled by AuthProvider/Middleware
    // const session = await getSession();
    // if (!session) redirect("/auth/login");

    const { slug } = await params;

    return <DashboardLayout appSlug={slug}>{children}</DashboardLayout>;
}
