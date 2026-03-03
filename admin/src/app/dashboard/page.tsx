'use client'

import * as React from 'react'
import { Activity, AlertTriangle, Key, Loader2, Shield, Users, Zap } from 'lucide-react'
import DashboardLayout from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'

interface AccountSummary {
  id: number
  email: string
  name: string | null
  tier: string
  status: string
  is_current: boolean
  proxy_disabled: boolean
  validation_blocked: boolean
  last_used: string | null
}

interface DashboardData {
  totalAccounts: number
  activeAccounts: number
  disabledAccounts: number
  errorAccounts: number
  forbiddenAccounts: number
  currentAccount: AccountSummary | null
  recentAccounts: AccountSummary[]
}

export default function DashboardPage() {
  const [data, setData] = React.useState<DashboardData>({
    totalAccounts: 0,
    activeAccounts: 0,
    disabledAccounts: 0,
    errorAccounts: 0,
    forbiddenAccounts: 0,
    currentAccount: null,
    recentAccounts: [],
  })
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const [accountsRes, currentRes] = await Promise.all([
          api.get<{ items: AccountSummary[]; total: number }>(
            '/api/admin/accounts?page=1&page_size=100',
          ),
          api.get<{ account: AccountSummary | null }>('/api/admin/accounts/current'),
        ])

        const accounts = accountsRes.items || []
        const total = accountsRes.total || 0
        const active = accounts.filter((a) => a.status === 'active').length
        const disabled = accounts.filter((a) => a.status === 'disabled').length
        const error = accounts.filter((a) => a.status === 'error').length
        const forbidden = accounts.filter((a) => a.status === 'forbidden').length

        setData({
          totalAccounts: total,
          activeAccounts: active,
          disabledAccounts: disabled,
          errorAccounts: error,
          forbiddenAccounts: forbidden,
          currentAccount: currentRes.account,
          recentAccounts: accounts.slice(0, 5),
        })
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const stats = [
    {
      title: 'Total Accounts',
      value: data.totalAccounts,
      description: 'All registered accounts',
      icon: Users,
    },
    {
      title: 'Active Accounts',
      value: data.activeAccounts,
      description: 'Currently active',
      icon: Activity,
    },
    {
      title: 'Forbidden',
      value: data.forbiddenAccounts,
      description: 'Rate limited',
      icon: AlertTriangle,
    },
    {
      title: 'API Keys',
      value: '0',
      description: 'Active keys',
      icon: Key,
    },
  ]

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your iProxy system</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title} className="border-0 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className="rounded-lg bg-primary/10 p-2">
                  <stat.icon className="h-4 w-4 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {/* Current Account */}
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Current Account</CardTitle>
            </CardHeader>
            <CardContent>
              {data.currentAccount ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{data.currentAccount.email}</span>
                    <Badge
                      variant={data.currentAccount.status === 'active' ? 'success' : 'destructive'}
                    >
                      {data.currentAccount.status}
                    </Badge>
                  </div>
                  {data.currentAccount.name && (
                    <p className="text-sm text-muted-foreground">{data.currentAccount.name}</p>
                  )}
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{data.currentAccount.tier}</Badge>
                    <Badge variant={data.currentAccount.proxy_disabled ? 'destructive' : 'success'}>
                      Proxy: {data.currentAccount.proxy_disabled ? 'Off' : 'On'}
                    </Badge>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No account selected</p>
              )}
            </CardContent>
          </Card>

          {/* System Status */}
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">API Server</span>
                  <span className="flex items-center gap-2 text-sm">
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-green-600 font-medium">Online</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Database</span>
                  <span className="flex items-center gap-2 text-sm">
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-green-600 font-medium">Connected</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Accounts</span>
                  <span className="text-sm font-medium">
                    {data.activeAccounts} / {data.totalAccounts}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Error / Forbidden</span>
                  <span className="text-sm font-medium text-orange-500">
                    {data.errorAccounts + data.forbiddenAccounts}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Accounts */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Recent Accounts</CardTitle>
          </CardHeader>
          <CardContent>
            {data.recentAccounts.length === 0 ? (
              <p className="text-sm text-muted-foreground">No accounts yet</p>
            ) : (
              <div className="space-y-3">
                {data.recentAccounts.map((account) => (
                  <div key={account.id} className="flex items-center justify-between py-2">
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-2 w-2 rounded-full ${
                          account.status === 'active'
                            ? 'bg-green-500'
                            : account.status === 'forbidden'
                              ? 'bg-orange-500'
                              : account.status === 'error'
                                ? 'bg-red-500'
                                : 'bg-gray-400'
                        }`}
                      />
                      <div>
                        <p className="text-sm font-medium">{account.email}</p>
                        {account.name && (
                          <p className="text-xs text-muted-foreground">{account.name}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{account.tier}</Badge>
                      {account.is_current && <Badge variant="success">Current</Badge>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
