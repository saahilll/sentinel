import AppsListContent from "./AppsListContent";
import StandaloneShell from "@/components/dashboard/StandaloneShell";

export const metadata = {
    title: "Apps | Sentinel",
    description: "Manage your apps",
};

export default function AppsPage() {
    return (
        <StandaloneShell>
            <AppsListContent />
        </StandaloneShell>
    );
}
