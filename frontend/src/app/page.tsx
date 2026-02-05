"use client";

import { signIn, signOut, useSession } from "next-auth/react";

export default function Home() {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return <div className="p-10 text-center">Loading Sentinel...</div>;
  }

  const handleSync = async () => {
    const token = session?.accessToken; 

    if (!token) {
      alert("Error: No Access Token found.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8080/api/auth/sync", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        alert(`SUCCESS! \nUser ID: ${data.id}\nEmail: ${data.email}`);
      } else {
        alert("Failed to Sync: " + res.status);
      }
    } catch (err) {
      console.error(err);
      alert("Error: Backend unreachable.");
    }
  };

  if (!session) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 gap-4">
        <h1 className="text-3xl font-bold text-black">Sentinel Login</h1>
        <button
          onClick={() => signIn("auth0")}
          className="rounded bg-blue-600 px-8 py-3 font-bold text-white hover:bg-blue-700"
        >
          Log In with Auth0
        </button>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white gap-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-black">Welcome, {session.user?.name}</h1>
      </div>

      <div className="flex gap-4">
        <button
          onClick={handleSync}
          className="rounded bg-green-600 px-6 py-3 font-bold text-white hover:bg-green-700"
        >
          Sync with Java Backend
        </button>

        <button
          onClick={() => signOut()}
          className="rounded bg-red-500 px-6 py-3 font-bold text-white hover:bg-red-600"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}