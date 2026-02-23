"use client";

import { OrgProvider } from "@/components/providers/OrgProvider";

export default function OrgLayout({ children }: { children: React.ReactNode }) {
    return <OrgProvider>{children}</OrgProvider>;
}
