"use client"

import * as React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Loader2, Mail } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import api from "@/lib/api"

const formSchema = z.object({
    email: z.string().min(1, { message: "Email is required." }).email({
        message: "Please enter a valid email address.",
    }),
    password: z.string().min(1, "Password is required.").min(8, {
        message: "Password must be at least 8 characters.",
    }),
})

export default function LoginPage() {
    const router = useRouter()
    const [isLoading, setIsLoading] = React.useState(false)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    })



    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const response = await api.post("/auth/login", {
                username: values.email,
                email: values.email,
                password: values.password,
            })
            const { access_token } = response.data
            localStorage.setItem("access_token", access_token)
            toast.success("Signed in successfully")
            router.push("/dashboard")
        } catch (error: any) {
            console.error(error)
            const message = error.response?.data?.detail || "Something went wrong."

            if (error.response?.status === 401) {
                form.setError("email", { message: "Invalid credentials" })
                form.setError("password", { message: "Invalid credentials" })
            } else {
                toast.error(message)
            }
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col space-y-2 text-center">
                <h1 className="text-2xl font-semibold tracking-tight text-white mb-2">Welcome back to Sentinel</h1>
                <p className="text-sm text-zinc-400">
                    Enter your credentials to access the platform
                </p>
            </div>

            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel className="text-zinc-400">Email</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="you@company.com"
                                        {...field}
                                        className="bg-black border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-600 h-10"
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel className="text-zinc-400">Password</FormLabel>
                                <FormControl>
                                    <Input
                                        type="password"
                                        placeholder="Enter your password"
                                        {...field}
                                        className="bg-black border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-600 h-10"
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2">
                            {/* Mock Checkbox for visual fidelity */}
                            <input type="checkbox" id="remember" className="rounded border-zinc-700 bg-zinc-900 data-[state=checked]:bg-blue-600" />
                            <label htmlFor="remember" className="text-zinc-400 font-medium cursor-pointer">Remember me</label>
                        </div>
                        <Link href="/forgot-password" className="text-zinc-500 hover:text-zinc-300">
                            Forgot password?
                        </Link>
                    </div>

                    <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium h-10" type="submit" disabled={isLoading}>
                        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Log in &rarr;
                    </Button>
                </form>
            </Form>

            <div className="relative">
                <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-zinc-800" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-black px-2 text-zinc-500">Or</span>
                </div>
            </div>

            <Button variant="outline" className="w-full border-zinc-800 text-zinc-300 hover:bg-zinc-900 hover:text-white bg-transparent h-10" disabled={isLoading}>
                <Mail className="mr-2 h-4 w-4" />
                Sign in with magic link
            </Button>
        </div>
    )
}
