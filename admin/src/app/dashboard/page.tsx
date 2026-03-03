import DashboardLayout from "@/components/layout/dashboard-layout"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div>
        <h1 className="mb-6 text-2xl font-semibold">Dashboard</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <div className="text-sm text-muted-foreground">Total Accounts</div>
            <div className="mt-2 text-3xl font-semibold">0</div>
          </div>
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <div className="text-sm text-muted-foreground">Active Accounts</div>
            <div className="mt-2 text-3xl font-semibold">0</div>
          </div>
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <div className="text-sm text-muted-foreground">Total Requests</div>
            <div className="mt-2 text-3xl font-semibold">0</div>
          </div>
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <div className="text-sm text-muted-foreground">API Keys</div>
            <div className="mt-2 text-3xl font-semibold">0</div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
