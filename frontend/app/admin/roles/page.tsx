"use client"

import { useEffect, useState } from "react"
import { DataTable } from "@/components/ui/DataTable"
import { Modal } from "@/components/ui/Modal"

type Role = {
  id: string
  name: string
  permissions: string[]
}

const allPermissions = [
  "read_users",
  "write_users",
  "read_roles",
  "write_roles",
  "read_content",
  "write_content",
  "read_logs",
  "read_settings"
]

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([])
  const [selected, setSelected] = useState<Role | null>(null)

  const fetchRoles = () => {
    fetch("/api/admin/roles")
      .then(res => res.json())
      .then(setRoles)
  }

  useEffect(() => {
    fetchRoles()
  }, [])

  const handleDelete = async (id: string) => {
    if (confirm("Delete this role?")) {
      await fetch(`/api/admin/roles/${id}`, { method: "DELETE" })
      fetchRoles()
    }
  }

  const handleSave = async (e: any) => {
    e.preventDefault()
    const form = new FormData(e.target)
    const updated = {
      name: form.get("name"),
      permissions: allPermissions.filter(p => form.get(p) === "on")
    }
    await fetch(`/api/admin/roles/${selected?.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated)
    })
    setSelected(null)
    fetchRoles()
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Roles</h1>
      <DataTable
        headers={["id", "name"]}
        data={roles}
        actions={(r) => (
          <div className="flex gap-2 text-sm">
            <button onClick={() => setSelected(r)} className="text-blue-600 hover:underline">Edit</button>
            <button onClick={() => handleDelete(r.id)} className="text-red-600 hover:underline">Delete</button>
          </div>
        )}
      />

      <Modal isOpen={!!selected} onClose={() => setSelected(null)}>
        <h2 className="text-lg font-semibold mb-2">Edit Role</h2>
        {selected && (
          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Name</label>
              <input name="name" defaultValue={selected.name} className="w-full border rounded px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Permissions</label>
              <div className="grid grid-cols-2 gap-2">
                {allPermissions.map((perm) => (
                  <label key={perm} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      name={perm}
                      defaultChecked={selected.permissions.includes(perm)}
                    />
                    {perm}
                  </label>
                ))}
              </div>
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
