"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check session via BFF endpoint
    fetch("/api/auth/me", { credentials: "include" })
      .then((res) => {
        if (res.ok) {
          router.push("/dashboard")
        } else {
          router.push("/login")
        }
      })
      .catch(() => {
        router.push("/login")
      })
  }, [router])

  return (
    <div className="flex h-screen items-center justify-center bg-black text-white">
      <p>Redirecting...</p>
    </div>
  )
}