"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { DataTable } from "@/components/ui/DataTable"
import { Modal } from "@/components/ui/Modal"

const schema = z.object({
  title: z.string().min(3),
  status: z.enum(["draft", "published"])
})

type ContentItem = {
  id: string
  title: string
  status: string
  createdAt: string
}

export default function ContentPage() {
  const [items, setItems] = useState<ContentItem[]>([])
  const [selected, setSelected] = useState<ContentItem | null>(null)
  const [adding, setAdding] = useState(false)
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema)
  })

  const fetchItems = () => {
    fetch("/api/admin/content")
      .then(res => res.json())
      .then(setItems)
  }

  useEffect(() => {
    fetchItems()
  }, [])

  const handleDelete = async (id: string) => {
    if (confirm("Delete content item?")) {
      await fetch(`/api/admin/content/${id}`, { method: "DELETE" })
      fetchItems()
    }
  }

  const handleSave = async (data: any) => {
    const method = selected ? "PATCH" : "POST"
    const url = selected ? `/api/admin/content/${selected.id}` : "/api/admin/content"
    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
    setSelected(null)
    setAdding(false)
    fetchItems()
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Content</h1>
        <button
          onClick={() => {
            setSelected(null)
            setAdding(true)
            reset()
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Add New
        </button>
      </div>

      <DataTable
        headers={["id", "title", "status", "createdAt"]}
        data={items}
        actions={(item) => (
          <div className="flex gap-2 text-sm">
            <button onClick={() => { setSelected(item); reset(item) }} className="text-blue-600 hover:underline">Edit</button>
            <button onClick={() => handleDelete(item.id)} className="text-red-600 hover:underline">Delete</button>
          </div>
        )}
      />

      {(adding || selected) && (
        <Modal isOpen={true} onClose={() => {
          setSelected(null)
          setAdding(false)
        }}>
          <h2 className="text-lg font-semibold mb-2">
            {selected ? "Edit Content" : "New Content"}
          </h2>
          <form onSubmit={handleSubmit(handleSave)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Title</label>
              <input {...register("title")} className="w-full border rounded px-3 py-2 mt-1" />
              {errors.title && <p className="text-red-500 text-sm">{errors.title.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Status</label>
              <select {...register("status")} className="w-full border rounded px-3 py-2 mt-1">
                <option value="draft">Draft</option>
                <option value="published">Published</option>
              </select>
              {errors.status && <p className="text-red-500 text-sm">{errors.status.message}</p>}
            </div>
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
              Save
            </button>
          </form>
        </Modal>
      )}
    </div>
  )
}
