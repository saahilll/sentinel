"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function Navbar() {
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            // Decode token or fetch user (simplified check)
            setUser({ loggedIn: true });
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("token");
        window.location.reload();
    };

    return (
        <nav className="bg-gray-800 p-4 text-white flex justify-between items-center">
            <Link href="/" className="text-xl font-bold">
                Sentinel
            </Link>
            <div>
                {user ? (
                    <button onClick={handleLogout} className="bg-red-500 px-3 py-1 rounded hover:bg-red-600">
                        Logout
                    </button>
                ) : (
                    <span className="text-sm">Not Logged In</span>
                )}
            </div>
        </nav>
    );
}
