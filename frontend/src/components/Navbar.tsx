"use client";

import { signIn, signOut, useSession } from "next-auth/react";
import Link from "next/link";

export default function Navbar() {
    const { data: session } = useSession();

    return (
        <nav className="flex items-center justify-between bg-gray-900 px-6 py-4 text-white shadow-md">
            <div className="text-xl font-bold tracking-wide">
                <Link href="/">Sentinel</Link>
            </div>

            <div className="flex items-center gap-4">
                {session ? (
                    <>
                        <span className="text-sm text-gray-300">
                            {session.user?.name || session.user?.email}
                        </span>
                        <button
                            onClick={() => signOut()}
                            className="rounded bg-red-600 px-4 py-2 text-sm font-semibold hover:bg-red-700 transition"
                        >
                            Log Out
                        </button>
                    </>
                ) : (
                    <button
                        onClick={() => signIn("auth0")}
                        className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-700 transition"
                    >
                        Log In
                    </button>
                )}
            </div>
        </nav>
    );
}
