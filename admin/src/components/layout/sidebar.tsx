"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Users,
  Shield,
  Activity,
  BarChart3,
  Key,
  Settings,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/accounts", label: "Accounts", icon: Users },
  { href: "/proxy", label: "Proxy", icon: Zap },
  { href: "/security", label: "Security", icon: Shield },
  { href: "/monitor", label: "Monitor", icon: Activity },
  { href: "/stats", label: "Stats", icon: BarChart3 },
  { href: "/keys", label: "API Keys", icon: Key },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex h-screen w-56 flex-col border-r bg-background">
      <div className="flex h-14 items-center border-b px-4">
        <span className="text-lg font-semibold">iProxy</span>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
              pathname.startsWith(href)
                ? "bg-accent text-accent-foreground font-medium"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}
