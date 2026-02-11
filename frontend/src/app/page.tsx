"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export default function Home() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      router.push("/dashboard")
    } else {
      router.push("/login")
    }
    // We don't really need to set loading false because we strictly redirect
    // But for safety:
    setLoading(false)
  }, [router])

  return (
    <div className="flex h-screen items-center justify-center bg-black text-white">
      <p>Redirecting...</p>
    </div>
  )
}