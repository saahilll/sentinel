"use client";

import { useEffect, useState } from "react";
import AuthForm from "../components/AuthForm";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) {
          const data = await res.json();
          setUser(data);
        } else {
          localStorage.removeItem("token"); // Invalid token
        }
      } catch (err) {
        console.error("Failed to fetch user", err);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) {
    return <div className="p-10 text-center">Loading Sentinel...</div>;
  }

  if (!user) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 gap-4">
        <h1 className="text-3xl font-bold text-black mb-8">Sentinel Login</h1>
        <AuthForm />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white gap-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-black">Welcome, {user.full_name || user.email}</h1>
        <p className="text-gray-500">Your ID: {user.email}</p>
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => {
            localStorage.removeItem("token");
            window.location.reload();
          }}
          className="rounded bg-red-500 px-6 py-3 font-bold text-white hover:bg-red-600"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}