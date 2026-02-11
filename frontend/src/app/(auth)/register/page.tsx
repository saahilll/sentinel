"use client"

import * as React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Loader2 } from "lucide-react"
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
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import { Info } from "lucide-react"
import api from "@/lib/api"

const formSchema = z.object({
    organization_name: z.string().min(1, "Organization name is required.").min(2, "Organization name must be at least 2 characters."),
    first_name: z.string().min(1, "First name is required."),
    last_name: z.string().optional(),
    email: z.string().min(1, "Email is required.").email("Please enter a valid email address."),
    password: z.string()
        .min(1, "Password is required.")
        .min(8, "Password must be at least 8 characters.")
        .regex(/[A-Z]/, "Password must contain at least one uppercase letter.")
        .regex(/[a-z]/, "Password must contain at least one lowercase letter.")
        .regex(/[0-9]/, "Password must contain at least one number.")
        .regex(/[^A-Za-z0-9]/, "Password must contain at least one special character."),
})

export default function RegisterPage() {
    const router = useRouter()
    const [isLoading, setIsLoading] = React.useState(false)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            organization_name: "",
            first_name: "",
            last_name: "",
            email: "",
            password: "",
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)

        try {
            const response = await api.post("/auth/register", {
                organization_name: values.organization_name,
                first_name: values.first_name,
                last_name: values.last_name || null,
                email: values.email,
                password: values.password,
                invites: [] // No invites during initial registration for now
            })

            const { access_token } = response.data

            // Store token
            localStorage.setItem("access_token", access_token)

            toast.success("Account created successfully")
            router.push("/dashboard")

        } catch (error: any) {
            console.error(error)
            const message = error.response?.data?.detail || "Something went wrong. Please try again."

            if (error.response?.status === 409) {
                form.setError("email", { message: "This email is already registered." })
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
                <h1 className="text-2xl font-semibold tracking-tight text-white mb-2">Start your 14-day trial</h1>
                <p className="text-sm text-zinc-400">
                    Join thousands of enterprises trusting Sentinel for ITSM
                </p>
            </div>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        control={form.control}
                        name="organization_name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel className="text-zinc-400">Organization Name</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="Acme Inc."
                                        {...field}
                                        className="bg-black border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-600 h-10"
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <div className="grid grid-cols-2 gap-4">
                        <FormField
                            control={form.control}
                            name="first_name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel className="text-zinc-400">First Name</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="John"
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
                            name="last_name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel className="text-zinc-400">Last Name</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="Doe"
                                            {...field}
                                            className="bg-black border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-600 h-10"
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel className="text-zinc-400">Email</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="name@example.com"
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
                                <div className="flex items-center gap-2">
                                    <FormLabel className="text-zinc-400">Password</FormLabel>
                                    <TooltipProvider>
                                        <Tooltip>
                                            <TooltipTrigger type="button">
                                                <Info className="h-4 w-4 text-zinc-500 hover:text-zinc-300 transition-colors" />
                                            </TooltipTrigger>
                                            <TooltipContent className="bg-zinc-900 border-zinc-800 text-zinc-300 p-3">
                                                <div className="space-y-2">
                                                    <p className="font-medium text-white text-xs">Password Requirements:</p>
                                                    <ul className="text-xs list-disc pl-4 space-y-1">
                                                        <li>At least 8 characters</li>
                                                        <li>At least one uppercase letter</li>
                                                        <li>At least one lowercase letter</li>
                                                        <li>At least one number</li>
                                                        <li>At least one special character</li>
                                                    </ul>
                                                </div>
                                            </TooltipContent>
                                        </Tooltip>
                                    </TooltipProvider>
                                </div>
                                <FormControl>
                                    <Input
                                        type="password"
                                        placeholder="Create a password"
                                        {...field}
                                        className="bg-black border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-600 h-10"
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium h-10" type="submit" disabled={isLoading}>
                        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Create Account &rarr;
                    </Button>
                </form>
            </Form>
            <div className="px-8 text-center text-sm text-zinc-500">
                <Link
                    href="/login"
                    className="hover:text-white underline underline-offset-4"
                >
                    Already have an account? Sign In
                </Link>
            </div>
        </div>
    )
}
