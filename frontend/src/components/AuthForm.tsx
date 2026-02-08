"use client";

import { useState } from "react";

export default function AuthForm() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [fullName, setFullName] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register";
        const body = isLogin
            ? { email, password }
            : { email, password, full_name: fullName };

        try {
            const res = await fetch(`http://localhost:8000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || "Something went wrong");
            }

            if (isLogin) {
                localStorage.setItem("token", data.access_token);
                window.location.reload(); // Refresh to update UI state
            } else {
                alert("Registration successful! Please login.");
                setIsLogin(true);
            }
        } catch (err: any) {
            setError(err.message);
        }
    };

    return (
        <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
                {isLogin ? "Login" : "Register"}
            </h2>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Full Name</label>
                        <input
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                            required
                        />
                    </div>
                )}

                <div>
                    <label className="block text-sm font-medium text-gray-700">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                        required
                    />
                </div>

                <button
                    type="submit"
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                    {isLogin ? "Sign In" : "Sign Up"}
                </button>
            </form>

            <div className="mt-4 text-center">
                <button
                    onClick={() => setIsLogin(!isLogin)}
                    className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                >
                    {isLogin ? "Need an account? Register" : "Already have an account? Login"}
                </button>
            </div>
        </div>
    );
}
