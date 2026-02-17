"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Monitor, LogOut } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DashboardPage() {
    const router = useRouter()
    const [user, setUser] = useState<{ email: string } | null>(null)

    useEffect(() => {
        // Check session via BFF endpoint
        fetch("/api/auth/me", { credentials: "include" })
            .then(async (res) => {
                if (!res.ok) {
                    router.push("/login")
                    return
                }
                const data = await res.json()
                setUser({ email: data.email })
            })
            .catch(() => {
                router.push("/login")
            })
    }, [router])

    const handleLogout = async () => {
        await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "include",
        })
        router.push("/login")
    }

    if (!user) {
        return null // Or a loading spinner
    }

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <header className="flex items-center justify-between mb-8 max-w-5xl mx-auto">
                <div className="flex items-center space-x-2">
                    <Monitor className="h-6 w-6 text-blue-500" />
                    <h1 className="text-xl font-bold">Sentinel Dashboard</h1>
                </div>
                <Button variant="outline" onClick={handleLogout} className="border-zinc-800 hover:bg-zinc-900 text-zinc-300">
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                </Button>
            </header>

            <main className="max-w-5xl mx-auto grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <Card className="bg-zinc-900 border-zinc-800 text-white">
                    <CardHeader>
                        <CardTitle>Overview</CardTitle>
                        <CardDescription className="text-zinc-400">System Status</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-500">Operational</div>
                        <p className="text-sm text-zinc-500 mt-2">All systems running smoothly.</p>
                    </CardContent>
                </Card>

                {/* Placeholder cards */}
                <Card className="bg-zinc-900 border-zinc-800 text-white opacity-50">
                    <CardHeader><CardTitle>Incidents</CardTitle></CardHeader>
                    <CardContent>Coming Soon</CardContent>
                </Card>
                <Card className="bg-zinc-900 border-zinc-800 text-white opacity-50">
                    <CardHeader><CardTitle>Monitors</CardTitle></CardHeader>
                    <CardContent>Coming Soon</CardContent>
                </Card>
            </main>
        </div>
    )
}
