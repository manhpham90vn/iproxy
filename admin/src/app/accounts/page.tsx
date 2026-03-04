'use client'

import * as React from 'react'
import {
  Check,
  Download,
  Filter,
  Loader2,
  MoreHorizontal,
  Play,
  RefreshCw,
  Search,
  Shield,
  ShieldOff,
  Trash2,
  Upload,
  Zap,
} from 'lucide-react'


import { api } from '@/lib/api'
import DashboardLayout from '@/components/layout/dashboard-layout'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface Account {
  id: number
  email: string
  name: string | null
  label: string | null
  custom_label: string | null
  tier: 'free' | 'pro' | 'ultra'
  status: 'active' | 'disabled' | 'error' | 'forbidden'
  is_current: boolean
  sort_order: number
  token_expiry: string | null
  proxy_id: number | null
  proxy_disabled: boolean
  proxy_disabled_reason: string | null
  disabled_reason: string | null
  validation_blocked: boolean
  validation_blocked_until: string | null
  validation_blocked_reason: string | null
  validation_url: string | null
  protected_models: string[]
  quota: {
    models: Array<{
      name: string
      percentage: number
      display_name?: string
      supports_images?: boolean
      supports_thinking?: boolean
      thinking_budget?: number
      recommended?: boolean
      max_tokens?: number
    }>
    last_updated: string | null
    is_forbidden: boolean
    forbidden_reason: string | null
    subscription_tier: string | null
  } | null
  last_used: string | null
  created_at: string
  updated_at: string
  fingerprint: {
    id: number
    account_id: number
    machine_id: string | null
    mac_machine_id: string | null
    dev_device_id: string | null
    sqm_id: string | null
    user_agent: string | null
    accept_language: string | null
    platform: string | null
    data: string | null
  } | null
}

interface AccountListResponse {
  items: Account[]
  total: number
  page: number
  page_size: number
}

const tierColors = {
  free: 'secondary',
  pro: 'warning',
  ultra: 'success',
} as const

const statusColors = {
  active: 'success',
  disabled: 'secondary',
  error: 'destructive',
  forbidden: 'warning',
} as const

export default function AccountsPage() {
  const [accounts, setAccounts] = React.useState<Account[]>([])
  const [total, setTotal] = React.useState(0)
  const [page, setPage] = React.useState(1)
  const [pageSize] = React.useState(20)
  const [loading, setLoading] = React.useState(true)
  const [search, setSearch] = React.useState('')
  const [tierFilter, setTierFilter] = React.useState<string>('all')
  const [statusFilter, setStatusFilter] = React.useState<string>('all')
  const [selectedAccounts, setSelectedAccounts] = React.useState<Set<number>>(new Set())

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = React.useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = React.useState(false)
  const importFileRef = React.useRef<HTMLInputElement>(null)
  const [selectedAccount, setSelectedAccount] = React.useState<Account | null>(null)
  const [formData, setFormData] = React.useState({
    email: '',
    name: '',
    label: '',
    custom_label: '',
    tier: 'free',
  })
  const [actionLoading, setActionLoading] = React.useState(false)
  const [warmupLoading, setWarmupLoading] = React.useState<Set<number>>(new Set())
  const [isProtectedModelsDialogOpen, setIsProtectedModelsDialogOpen] = React.useState(false)
  const [isValidationBlockDialogOpen, setIsValidationBlockDialogOpen] = React.useState(false)
  const [protectedModelsInput, setProtectedModelsInput] = React.useState('')
  const [validationBlockForm, setValidationBlockForm] = React.useState({
    blocked: true,
    reason: '',
    url: '',
    until: '',
  })
  const [logDialog, setLogDialog] = React.useState<{ open: boolean; title: string; lines: { label: string; value: string; ok?: boolean }[] }>({
    open: false,
    title: '',
    lines: [],
  })

  const fetchAccounts = React.useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)
      if (tierFilter !== 'all') params.append('tier', tierFilter)
      if (statusFilter !== 'all') params.append('status', statusFilter)

      const data = await api.get<AccountListResponse>(`/api/admin/accounts?${params}`)
      setAccounts(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch accounts:', error)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, search, tierFilter, statusFilter])

  React.useEffect(() => {
    fetchAccounts()
  }, [fetchAccounts])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchAccounts()
  }

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedAccounts(new Set(accounts.map((a) => a.id)))
    } else {
      setSelectedAccounts(new Set())
    }
  }

  const handleSelectAccount = (id: number) => {
    const newSelected = new Set(selectedAccounts)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedAccounts(newSelected)
  }



  const handleEdit = async () => {
    if (!selectedAccount) return
    setActionLoading(true)
    try {
      await api.put(`/api/admin/accounts/${selectedAccount.id}`, {
        name: formData.name || null,
        label: formData.label || null,
        custom_label: formData.custom_label || null,
        tier: formData.tier,
      })
      setIsEditDialogOpen(false)
      setSelectedAccount(null)
      fetchAccounts()
    } catch (error) {
      console.error('Failed to update account:', error)
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async () => {
    if (selectedAccounts.size === 0) return
    setActionLoading(true)
    try {
      await api.post('/api/admin/accounts/batch-delete', {
        account_ids: Array.from(selectedAccounts),
      })
      setIsDeleteDialogOpen(false)
      setSelectedAccounts(new Set())
      fetchAccounts()
    } catch (error) {
      console.error('Failed to delete accounts:', error)
    } finally {
      setActionLoading(false)
    }
  }

  const handleRefresh = async (id: number, email: string) => {
    try {
      const data = await api.post<{ account: Account; log: Record<string, unknown> }>(`/api/admin/accounts/${id}/refresh-quota`)
      fetchAccounts()
      const log = data.log || {}
      setLogDialog({
        open: true,
        title: `Refresh Quota — ${email}`,
        lines: [
          { label: 'Status', value: log.success ? '✅ Success' : '❌ Failed', ok: Boolean(log.success) },
          { label: 'Subscription', value: String(log.subscription_tier ?? 'N/A') },
          { label: 'Models fetched', value: String(log.models_count ?? 0) },
          ...(log.error ? [{ label: 'Error', value: String(log.error), ok: false }] : []),
        ],
      })
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : String(error)
      setLogDialog({ open: true, title: `Refresh Quota — ${email}`, lines: [{ label: 'Error', value: msg, ok: false }] })
    }
  }

  const handleSwitchAccount = async (id: number) => {
    try {
      await api.post(`/api/admin/accounts/switch-account?account_id=${id}`)
      fetchAccounts()
    } catch (error) {
      console.error('Failed to switch account:', error)
    }
  }

  const handleWarmup = async (id: number, email: string) => {
    setWarmupLoading((prev) => new Set(prev).add(id))
    try {
      const data = await api.post<{ account_id: number; status: string; message: string; is_forbidden: boolean }>(`/api/admin/accounts/${id}/warmup`)
      fetchAccounts()
      setLogDialog({
        open: true,
        title: `Warmup — ${email}`,
        lines: [
          { label: 'Status', value: data.status === 'success' ? '✅ Success' : `❌ ${data.status}`, ok: data.status === 'success' },
          { label: 'Message', value: data.message },
          { label: 'Forbidden', value: data.is_forbidden ? 'Yes' : 'No', ok: !data.is_forbidden },
        ],
      })
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : String(error)
      setLogDialog({ open: true, title: `Warmup — ${email}`, lines: [{ label: 'Error', value: msg, ok: false }] })
    } finally {
      setWarmupLoading((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const handleSetProtectedModels = async () => {
    if (!selectedAccount) return
    setActionLoading(true)
    try {
      const models = protectedModelsInput
        .split(',')
        .map((m) => m.trim())
        .filter(Boolean)
      await api.put(`/api/admin/accounts/${selectedAccount.id}/protected-models`, { models })
      setIsProtectedModelsDialogOpen(false)
      fetchAccounts()
    } catch (error) {
      console.error('Failed to set protected models:', error)
    } finally {
      setActionLoading(false)
    }
  }

  const handleSetValidationBlock = async () => {
    if (!selectedAccount) return
    setActionLoading(true)
    try {
      await api.post(`/api/admin/accounts/${selectedAccount.id}/validation-block`, {
        blocked: validationBlockForm.blocked,
        reason: validationBlockForm.reason || null,
        url: validationBlockForm.url || null,
        until: validationBlockForm.until || null,
      })
      setIsValidationBlockDialogOpen(false)
      fetchAccounts()
    } catch (error) {
      console.error('Failed to set validation block:', error)
    } finally {
      setActionLoading(false)
    }
  }

  const handleBatchRefresh = async () => {
    if (selectedAccounts.size === 0) return
    try {
      await api.post('/api/admin/accounts/batch-refresh', {
        account_ids: Array.from(selectedAccounts),
      })
      setSelectedAccounts(new Set())
      fetchAccounts()
    } catch (error) {
      console.error('Failed to refresh tokens:', error)
    }
  }

  const handleBatchWarmup = async () => {
    if (selectedAccounts.size === 0) return
    try {
      await api.post('/api/admin/accounts/batch-warmup', {
        account_ids: Array.from(selectedAccounts),
      })
      setSelectedAccounts(new Set())
      fetchAccounts()
    } catch (error) {
      console.error('Failed to batch warmup:', error)
    }
  }

  const handleRefreshAll = async () => {
    try {
      await api.post('/api/admin/accounts/refresh-all')
      fetchAccounts()
    } catch (error) {
      console.error('Failed to refresh all:', error)
    }
  }

  const handleWarmupAll = async () => {
    try {
      await api.post('/api/admin/accounts/warmup-all')
      fetchAccounts()
    } catch (error) {
      console.error('Failed to warmup all:', error)
    }
  }

  const handleExport = async () => {
    try {
      type ExportAccount = { email: string; refresh_token: string | null }
      const data = await api.get<{ accounts: ExportAccount[] }>('/api/admin/accounts/export')
      const simplified = data.accounts.map((acc) => ({
        email: acc.email,
        refresh_token: acc.refresh_token,
      }))
      const blob = new Blob([JSON.stringify(simplified, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'accounts.json'
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export accounts:', error)
    }
  }

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    // Reset input so same file can be selected again
    e.target.value = ''
    setActionLoading(true)
    try {
      const text = await file.text()
      const parsed = JSON.parse(text)
      // Support both array format [{email, refresh_token}] and export wrapper {accounts: [...]}
      const accounts = Array.isArray(parsed) ? parsed : parsed.accounts
      await api.post('/api/admin/accounts/import', { accounts })
      fetchAccounts()
    } catch (error) {
      console.error('Failed to import accounts:', error)
      alert('Import failed: invalid JSON file')
    } finally {
      setActionLoading(false)
    }
  }

  const handleOAuth = async () => {
    setActionLoading(true)
    try {
      const data = await api.get<{ url: string }>('/api/admin/accounts/oauth/url')
      // Open OAuth URL in new window
      window.open(data.url, '_blank', 'width=500,height=600')

      // Listen for OAuth result from popup
      const handleOAuthMessage = (event: MessageEvent) => {
        if (event.data.type === 'oauth_success') {
          console.log('OAuth success:', event.data)
          fetchAccounts()
        } else if (event.data.type === 'oauth_error') {
          console.error('OAuth error:', event.data.error)
          alert(`OAuth failed: ${event.data.error}`)
        }
      }

      window.addEventListener('message', handleOAuthMessage)

      // Cleanup after a timeout
      setTimeout(() => {
        window.removeEventListener('message', handleOAuthMessage)
        setActionLoading(false)
      }, 5000)
    } catch (error) {
      console.error('Failed to get OAuth URL:', error)
      alert(`Failed to start OAuth: ${error}`)
      setActionLoading(false)
    }
  }

  const openEditDialog = (account: Account) => {
    setSelectedAccount(account)
    setFormData({
      email: account.email,
      name: account.name || '',
      label: account.label || '',
      custom_label: account.custom_label || '',
      tier: account.tier,
    })
    setIsEditDialogOpen(true)
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Accounts</h1>
            <p className="text-sm text-muted-foreground">Manage your Google accounts</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleRefreshAll} disabled={actionLoading}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh All
            </Button>
            <Button variant="outline" size="sm" onClick={handleWarmupAll} disabled={actionLoading}>
              <Zap className="mr-2 h-4 w-4" />
              Warmup All
            </Button>
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <>
              <input
                ref={importFileRef}
                type="file"
                accept=".json"
                className="hidden"
                onChange={handleImportFile}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => importFileRef.current?.click()}
                disabled={actionLoading}
              >
                <Upload className="mr-2 h-4 w-4" />
                Import
              </Button>
            </>
            <Button variant="outline" size="sm" onClick={handleOAuth}>
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
              Login Google
            </Button>

          </div>
        </div>

        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <CardTitle className="text-base">Account List</CardTitle>
              <form onSubmit={handleSearch} className="flex gap-2">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search accounts..."
                    className="pl-8"
                    style={{ width: 200 }}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <Select value={tierFilter} onValueChange={setTierFilter}>
                  <SelectTrigger style={{ width: 120 }}>
                    <Filter className="mr-2 h-4 w-4" />
                    <SelectValue placeholder="Tier" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Tiers</SelectItem>
                    <SelectItem value="free">Free</SelectItem>
                    <SelectItem value="pro">Pro</SelectItem>
                    <SelectItem value="ultra">Ultra</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger style={{ width: 130 }}>
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="disabled">Disabled</SelectItem>
                    <SelectItem value="error">Error</SelectItem>
                    <SelectItem value="forbidden">Forbidden</SelectItem>
                  </SelectContent>
                </Select>
                <Button type="submit" variant="secondary" size="sm">
                  Filter
                </Button>
              </form>
            </div>
          </CardHeader>
          <CardContent>
            {selectedAccounts.size > 0 && (
              <div className="mb-4 flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {selectedAccounts.size} selected
                </span>
                <Button variant="outline" size="sm" onClick={handleBatchRefresh}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh Quota
                </Button>
                <Button variant="outline" size="sm" onClick={handleBatchWarmup}>
                  <Zap className="mr-2 h-4 w-4" />
                  Warmup
                </Button>
                <Button variant="destructive" size="sm" onClick={() => setIsDeleteDialogOpen(true)}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              </div>
            )}

            {loading ? (
              <div className="flex h-64 items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input
                        type="checkbox"
                        checked={selectedAccounts.size === accounts.length && accounts.length > 0}
                        onChange={handleSelectAll}
                        className="h-4 w-4"
                      />
                    </TableHead>
                    <TableHead className="w-12">Current</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Tier</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Proxy</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {accounts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} className="h-32 text-center text-muted-foreground">
                        No accounts found
                      </TableCell>
                    </TableRow>
                  ) : (
                    accounts.map((account) => (
                      <TableRow key={account.id}>
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={selectedAccounts.has(account.id)}
                            onChange={() => handleSelectAccount(account.id)}
                            className="h-4 w-4"
                          />
                        </TableCell>
                        <TableCell>
                          {account.is_current && <Check className="h-4 w-4 text-green-500" />}
                        </TableCell>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <span>{account.email}</span>
                            {account.custom_label && (
                              <span className="text-xs text-muted-foreground">
                                ({account.custom_label})
                              </span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{account.name || '-'}</TableCell>
                        <TableCell>
                          <Badge variant={tierColors[account.tier]}>{account.tier}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={statusColors[account.status]}>{account.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={account.proxy_disabled ? 'destructive' : 'success'}>
                            {account.proxy_disabled ? 'Disabled' : 'Enabled'}
                          </Badge>
                        </TableCell>
                        <TableCell>{new Date(account.created_at).toLocaleDateString()}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            {!account.is_current && (
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleSwitchAccount(account.id)}
                                title="Switch to this account"
                              >
                                <Play className="h-4 w-4" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRefresh(account.id, account.email)}
                              title="Refresh Quota"
                            >
                              <RefreshCw className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleWarmup(account.id, account.email)}
                              title="Warmup"
                              disabled={warmupLoading.has(account.id)}
                            >
                              {warmupLoading.has(account.id) ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Zap className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setSelectedAccount(account)
                                setProtectedModelsInput(account.protected_models.join(', '))
                                setIsProtectedModelsDialogOpen(true)
                              }}
                              title="Protected Models"
                            >
                              <Shield className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setSelectedAccount(account)
                                setValidationBlockForm({
                                  blocked: !account.validation_blocked,
                                  reason: account.validation_blocked_reason || '',
                                  url: account.validation_url || '',
                                  until: '',
                                })
                                setIsValidationBlockDialogOpen(true)
                              }}
                              title={account.validation_blocked ? 'Unblock Account' : 'Block Account'}
                            >
                              <ShieldOff className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => openEditDialog(account)}
                              title="Edit"
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setSelectedAccounts(new Set([account.id]))
                                setIsDeleteDialogOpen(true)
                              }}
                              title="Delete"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}

            {totalPages > 1 && (
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of{' '}
                  {total} accounts
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>



      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Account</DialogTitle>
            <DialogDescription>Update account details</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Email</label>
              <Input value={formData.email} disabled />
            </div>
            <div className="grid gap-2">
              <label htmlFor="edit-name" className="text-sm font-medium">
                Name
              </label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Display name"
              />
            </div>
            <div className="grid gap-2">
              <label htmlFor="edit-label" className="text-sm font-medium">
                Label
              </label>
              <Input
                id="edit-label"
                value={formData.label}
                onChange={(e) => setFormData({ ...formData, label: e.target.value })}
                placeholder="Optional label"
              />
            </div>
            <div className="grid gap-2">
              <label htmlFor="edit-custom_label" className="text-sm font-medium">
                Custom Label
              </label>
              <Input
                id="edit-custom_label"
                value={formData.custom_label}
                onChange={(e) => setFormData({ ...formData, custom_label: e.target.value })}
                placeholder="Custom display label"
              />
            </div>
            <div className="grid gap-2">
              <label htmlFor="edit-tier" className="text-sm font-medium">
                Tier
              </label>
              <Select
                value={formData.tier}
                onValueChange={(value) => setFormData({ ...formData, tier: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="free">Free</SelectItem>
                  <SelectItem value="pro">Pro</SelectItem>
                  <SelectItem value="ultra">Ultra</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={actionLoading}>
              {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Accounts</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {selectedAccounts.size} account
              {selectedAccounts.size > 1 ? 's' : ''}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={actionLoading}>
              {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>



      {/* Protected Models Dialog */}
      <Dialog open={isProtectedModelsDialogOpen} onOpenChange={setIsProtectedModelsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Protected Models</DialogTitle>
            <DialogDescription>
              Set allowed models for {selectedAccount?.email}. Leave empty to allow all models.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Models (comma-separated)</label>
              <Input
                value={protectedModelsInput}
                onChange={(e) => setProtectedModelsInput(e.target.value)}
                placeholder="gemini-2.0-flash, gemini-1.5-pro"
              />
              <p className="text-xs text-muted-foreground">
                Current: {selectedAccount?.protected_models.length
                  ? selectedAccount.protected_models.join(', ')
                  : 'All models allowed'}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsProtectedModelsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSetProtectedModels} disabled={actionLoading}>
              {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Validation Block Dialog */}
      <Dialog open={isValidationBlockDialogOpen} onOpenChange={setIsValidationBlockDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {validationBlockForm.blocked ? 'Block Account' : 'Unblock Account'}
            </DialogTitle>
            <DialogDescription>
              {validationBlockForm.blocked
                ? `Block ${selectedAccount?.email} from being used`
                : `Unblock ${selectedAccount?.email}`}
            </DialogDescription>
          </DialogHeader>
          {validationBlockForm.blocked && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Reason</label>
                <Input
                  value={validationBlockForm.reason}
                  onChange={(e) =>
                    setValidationBlockForm({ ...validationBlockForm, reason: e.target.value })
                  }
                  placeholder="Reason for blocking"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Validation URL</label>
                <Input
                  value={validationBlockForm.url}
                  onChange={(e) =>
                    setValidationBlockForm({ ...validationBlockForm, url: e.target.value })
                  }
                  placeholder="https://..."
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Block Until (optional)</label>
                <Input
                  type="datetime-local"
                  value={validationBlockForm.until}
                  onChange={(e) =>
                    setValidationBlockForm({ ...validationBlockForm, until: e.target.value })
                  }
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsValidationBlockDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant={validationBlockForm.blocked ? 'destructive' : 'default'}
              onClick={handleSetValidationBlock}
              disabled={actionLoading}
            >
              {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {validationBlockForm.blocked ? 'Block' : 'Unblock'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Action Log Dialog */}
      <Dialog open={logDialog.open} onOpenChange={(open) => setLogDialog((prev) => ({ ...prev, open }))}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{logDialog.title}</DialogTitle>
          </DialogHeader>
          <div className="mt-2 space-y-2 rounded-md border bg-muted/40 p-3 text-sm font-mono">
            {logDialog.lines.map((line, i) => (
              <div key={i} className="flex gap-2">
                <span className="w-32 shrink-0 text-muted-foreground">{line.label}</span>
                <span
                  className={
                    line.ok === true
                      ? 'text-green-500'
                      : line.ok === false
                        ? 'text-red-400'
                        : 'text-foreground'
                  }
                >
                  {line.value}
                </span>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button onClick={() => setLogDialog((prev) => ({ ...prev, open: false }))}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
