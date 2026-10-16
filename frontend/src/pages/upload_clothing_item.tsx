import { useState, type FormEvent } from 'react'
import { createClothingItem } from '../api'

export function UploadPage({ onCreated }: { onCreated?: () => void }) {
  const [name, setName] = useState('')
  const [color, setColor] = useState('')
  const [size, setSize] = useState('')
  const [category, setCategory] = useState('')
  const [subcategory, setSubcategory] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!file) {
      setStatus('Choose an image')
      return
    }

    const body = new FormData()
    body.append('name', name)
    body.append('color', color)
    body.append('size', size)
    body.append('category', category)
    body.append('subcategory', subcategory)
    body.append('image', file) // field name must be "image"

    try {
      setStatus('Uploading…')
      const item = await createClothingItem(body)
      setStatus(`Created #${item.id}: ${item.name}`)
      onCreated?.() 
    } catch {
      setStatus('Upload failed')
    }
  }

  return (
    <main>
        <h1>Add clothing</h1>
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" required />
      <input value={color} onChange={(e) => setColor(e.target.value)} placeholder="Color" required />
      <input value={size} onChange={(e) => setSize(e.target.value)} placeholder="Size" required />
      <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Category" required />
      <input value={subcategory} onChange={(e) => setSubcategory(e.target.value)} placeholder="Subcategory" required />
      <input
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        required
      />
      <button type="submit">Add item</button>
      <p>{status}</p>
    </form>
    </main>
  )
}

