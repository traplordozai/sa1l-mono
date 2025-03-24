"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { DataTable } from "@/components/ui/DataTable"
import { Modal } from "@/components/ui/Modal"

type User = {
  id: string
  name: string
  email: string
  role: string
  status: string
}

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  role: z.string().min(1)
})

export default function UsersPage() {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema)
  })

  const [users, setUsers] = useState<User[]>([])
  const [selected, setSelected] = useState<User | null>(null)
  const [roles, setRoles] = useState<string[]>([])
  const { selectedIds, toggle, selectAll, clearAll, isSelected } = useBulkSelect(users)

  const impersonateUser = async (userId: string) => {
    const confirmed = confirm("Impersonate this user?")
    if (!confirmed) return
    await fetch(`/api/admin/impersonate/${userId}`, { method: "POST" })
    window.location.href = "/"
  }

  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const pageSize = 10

  const fetchUsers = () => {
    const query = new URLSearchParams({
      search,
      page: page.toString(),
      limit: pageSize.toString()
    }).toString()
    fetch(`/api/admin/users?${query}`)
      .then(res => res.json())
      .then((data) => {
        setUsers(data.users)
        setTotalPages(data.totalPages || 1)
      })
  }

  useEffect(() => {
    fetch("/api/admin/roles")
      .then(res => res.json())
      .then((data) => setRoles(data.map((r: any) => r.name)))

    fetchUsers()
  }, [page, search])

  const handleDelete = async (id: string) => {
    if (confirm("Delete user?")) {
      await fetch(`/api/admin/users/${id}`, { method: "DELETE" })
      fetchUsers()
    }
  }

  const handleSuspend = async (id: string) => {
    if (confirm("Suspend user?")) {
      await fetch(`/api/admin/users/${id}/suspend`, { method: "POST" })
      fetchUsers()
    }
  }

  const handleSave = async (e: any) => {
    e.preventDefault()
    const form = new FormData(e.target)
    const updated = {
      name: form.get("name"),
      email: form.get("email"),
      role: form.get("role")
    }
    await fetch(`/api/admin/users/${selected?.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated)
    })
    setSelected(null)
    fetchUsers()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Users</h1>
        <input
          className="border px-3 py-1 rounded text-sm"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <div className="flex gap-2 text-sm mb-2">
        <button onClick={selectAll} className="text-blue-600">Select All</button>
        <button onClick={clearAll} className="text-gray-600">Clear</button>
        {selectedIds.size > 0 && <>
          <button onClick={() => [...selectedIds].forEach(id => handleSuspend(id))} className="text-yellow-600">Bulk Suspend</button>
          <button onClick={() => [...selectedIds].forEach(id => handleDelete(id))} className="text-red-600">Bulk Delete</button>
        </>}
      </div>
      <DataTable
        headers={["id", "name", "email", "role", "status"]}
        data={users}
        actions={(u) => (
          <div className="flex gap-2 text-sm">
            <button onClick={() => setSelected(u)} className="text-blue-600 hover:underline">Edit</button>
            <button onClick={() => handleSuspend(u.id)} className="text-yellow-600 hover:underline">Suspend</button>
            <button onClick={() => impersonateUser(u.id)} className="text-indigo-600 hover:underline">Impersonate</button>
            <button onClick={() => handleDelete(u.id)} className="text-red-600 hover:underline">Delete</button>
          </div>
        )}
      />
      <div className="flex justify-between text-sm items-center pt-2">
        <button
          onClick={() => setPage((p) => Math.max(p - 1, 1))}
          disabled={page <= 1}
          className="text-blue-600 hover:underline disabled:text-gray-400"
        >
          ← Prev
        </button>
        <span>Page {page} of {totalPages}</span>
        <button
          onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
          disabled={page >= totalPages}
          className="text-blue-600 hover:underline disabled:text-gray-400"
        >
          Next →
        </button>
      </div>

      <Modal isOpen={!!selected} onClose={() => setSelected(null)}>
        <h2 className="text-lg font-semibold mb-2">Edit User</h2>
        {selected && (
          <form className="space-y-4" onSubmit={handleSubmit(handleSave)}>
            <div>
              <label className="block text-sm font-medium">Name</label>{errors.name && <p className="text-red-500 text-xs">{errors.name.message}</p>}
              <input  {...register("name")}  defaultValue={selected.name} className="w-full border rounded px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="block text-sm font-medium">Email</label>{errors.email && <p className="text-red-500 text-xs">{errors.email.message}</p>}
              <input  {...register("email")}  defaultValue={selected.email} className="w-full border rounded px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="block text-sm font-medium">Role</label>{errors.role && <p className="text-red-500 text-xs">{errors.role.message}</p>}
              <select  {...register("role")}  defaultValue={selected.role} className="w-full border rounded px-3 py-2 mt-1">
                {roles.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
              Save
            </button>
          </form>
        )}
      </Modal>
    </div>
  )
}
