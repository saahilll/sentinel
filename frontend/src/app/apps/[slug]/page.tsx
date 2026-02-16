import { redirect } from "next/navigation";

export default function AppIndexPage({ params }: { params: { slug: string } }) {
    // Default to endpoints view
    redirect(`/apps/${params.slug}/endpoints`);
}
