"use client";

import { useParams } from "next/navigation";
import { redirect } from "next/navigation";
import { use } from "react";

export default function SettingsPage({
    params,
}: {
    params: Promise<{ orgSlug: string }>;
}) {
    const { orgSlug } = use(params);
    redirect(`/${orgSlug}/settings/general`);
}
