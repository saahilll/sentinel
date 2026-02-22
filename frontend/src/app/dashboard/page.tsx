"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Monitor } from "lucide-react"
import Navbar from "@/components/dashboard/Navbar"

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
            <Navbar />

            <main className="max-w-5xl mx-auto grid gap-6 md:grid-cols-2 lg:grid-cols-3 mt-8">
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
