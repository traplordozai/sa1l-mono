import { ReactNode } from "react"

export function Modal({
  isOpen,
  onClose,
  children
}: {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
}) {
  if (!isOpen) return null
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow-lg max-w-lg w-full p-6">
        {children}
        <div className="mt-4 text-right">
          <button onClick={onClose} className="text-blue-600 hover:underline">Close</button>
        </div>
      </div>
    </div>
  )
}
