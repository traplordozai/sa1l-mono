import { z } from "zod"

export async function typedFetch<T>(url: string, schema: z.ZodType<T>, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, opts)
  const json = await res.json()
  return schema.parse(json)
}

// Example schema & usage
// const userSchema = z.object({ id: z.string(), name: z.string() })
// const user = await typedFetch("/api/admin/me", userSchema)
