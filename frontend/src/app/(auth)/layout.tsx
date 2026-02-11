import { Monitor, Shield, Globe } from "lucide-react"

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="container relative h-screen flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0 bg-black">
            {/* Left Panel - Marketing */}
            <div className="relative hidden h-full flex-col p-10 text-white lg:flex border-r border-zinc-800">
                <div className="absolute inset-0 bg-black" />

                {/* Logo */}
                <div className="relative z-20 flex items-center text-lg font-medium tracking-tight">
                    <span className="font-bold">Sentinel</span>
                </div>

                {/* Main Content */}
                <div className="relative z-20 mt-auto mb-auto">
                    <h1 className="text-5xl font-bold tracking-tighter mb-6 bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-transparent">
                        AI-Native Incident<br />Management at Scale.
                    </h1>
                    <p className="text-lg text-zinc-400 mb-12 max-w-md leading-relaxed">
                        Orchestrate response, automate triage, and maintain 99.99% uptime with the world's most advanced ITSM platform.
                    </p>

                    {/* Feature List */}
                    <div className="space-y-6">
                        <div className="flex items-center space-x-3 group">
                            <div className="p-2 rounded-full bg-blue-500/10 text-blue-500 group-hover:bg-blue-500/20 transition-colors">
                                <Monitor className="h-5 w-5" />
                            </div>
                            <span className="text-zinc-300 font-medium">Predictive Anomalies</span>
                        </div>
                        <div className="flex items-center space-x-3 group">
                            <div className="p-2 rounded-full bg-blue-500/10 text-blue-500 group-hover:bg-blue-500/20 transition-colors">
                                <Shield className="h-5 w-5" />
                            </div>
                            <span className="text-zinc-300 font-medium">Automated Root Cause Analysis</span>
                        </div>
                        <div className="flex items-center space-x-3 group">
                            <div className="p-2 rounded-full bg-blue-500/10 text-blue-500 group-hover:bg-blue-500/20 transition-colors">
                                <Globe className="h-5 w-5" />
                            </div>
                            <span className="text-zinc-300 font-medium">Global SLA Monitoring</span>
                        </div>
                    </div>
                </div>

                {/* Footer Links */}
                <div className="relative z-20 flex gap-6 text-sm text-zinc-500">
                    <a href="#" className="hover:text-zinc-300 transition-colors">Enterprise</a>
                    <a href="#" className="hover:text-zinc-300 transition-colors">Security</a>
                    <a href="#" className="hover:text-zinc-300 transition-colors">Contact Sales</a>
                </div>
            </div>

            {/* Right Panel - Form */}
            <div className="lg:p-8 flex items-center justify-center bg-black">
                <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[380px]">
                    {children}
                </div>
            </div>
        </div>
    )
}
