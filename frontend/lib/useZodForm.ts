import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { ZodSchema, z } from "zod"

export function useZodForm<T extends z.ZodTypeAny>(schema: T) {
  return useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    mode: "onSubmit"
  })
}
