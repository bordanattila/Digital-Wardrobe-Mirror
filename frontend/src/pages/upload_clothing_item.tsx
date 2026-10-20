import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { createClothingItem } from '../api'
import './upload_clothing_item.css'

const CLOTHING_CATEGORIES = {
  top: ['t_shirt', 'tank_top', 'long_sleeve', 'polo', 'blouse'],
  bottom: ['jeans', 'shorts', 'leggings', 'trousers', 'skirt'],
  mid_layer: ['hoodie', 'sweater', 'cardigan', 'fleece'],
  outer_layer: ['coat', 'jacket', 'raincoat', 'parka'],
  shoes: ['sneakers', 'sandals', 'boots', 'dress_shoes'],
} as const

type Category = keyof typeof CLOTHING_CATEGORIES

export function UploadPage({ onCreated }: { onCreated?: () => void }) {
  const [name, setName] = useState('')
  const [color, setColor] = useState('')
  const [size, setSize] = useState('')
  const [category, setCategory] = useState<Category>('top')
  const [subcategory, setSubcategory] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [status, setStatus] = useState('')
  const [statusKind, setStatusKind] = useState<'idle' | 'ok' | 'error'>('idle')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null)
      return
    }
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!file) {
      setStatus('Choose an image')
      setStatusKind('error')
      return
    }

    const body = new FormData()
    body.append('name', name)
    body.append('color', color)
    body.append('size', size)
    body.append('category', category)
    body.append('subcategory', subcategory)
    body.append('image', file)

    try {
      setIsSubmitting(true)
      setStatus('Uploading…')
      setStatusKind('idle')
      const item = await createClothingItem(body)
      setStatus(`Created #${item.id}: ${item.name}`)
      setStatusKind('ok')
      setName('')
      setColor('')
      setSize('')
      setCategory('top')
      setSubcategory('')
      setFile(null)
      onCreated?.()
    } catch {
      setStatus('Upload failed')
      setStatusKind('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const statusClass =
    statusKind === 'ok'
      ? 'upload-status upload-status--ok'
      : statusKind === 'error'
        ? 'upload-status upload-status--error'
        : 'upload-status'

  return (
    <main className="upload-page">
      <nav className="upload-nav">
        <Link to="/">Mirror</Link>
        <Link to="/full-wardrobe">Full wardrobe</Link>
      </nav>

      <header className="upload-header">
        <h1>Add clothing</h1>
        <p>Phone upload — photo plus a few tags for the mirror inventory.</p>
      </header>

      <form className="upload-form" onSubmit={handleSubmit}>
        <div className="upload-field">
          <label htmlFor="upload-name">Name</label>
          <input
            id="upload-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            required
            autoComplete="off"
          />
        </div>

        <div className="upload-field">
          <label htmlFor="upload-color">Color</label>
          <input
            id="upload-color"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            placeholder="Color"
            required
            autoComplete="off"
          />
        </div>

        <div className="upload-field">
          <label htmlFor="upload-size">Size</label>
          <input
            id="upload-size"
            value={size}
            onChange={(e) => setSize(e.target.value)}
            placeholder="Size"
            required
            autoComplete="off"
          />
        </div>

        <div className="upload-field">
          <label htmlFor="upload-category">Category</label>
          <select
            id="upload-category"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value)
              setSubcategory('')
            }}
            required
          >
            {Object.keys(CLOTHING_CATEGORIES).map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="upload-field">
          <label htmlFor="upload-subcategory">Subcategory</label>
          <select
            id="upload-subcategory"
            value={subcategory}
            onChange={(e) => setSubcategory(e.target.value)}
            required
          >
            <option value="" disabled>
              Select subcategory
            </option>
            {CLOTHING_CATEGORIES[category as keyof typeof CLOTHING_CATEGORIES].map((sub) => (
              <option key={sub} value={sub}>
                {sub.replaceAll('_', ' ')}  {/* label only */}
              </option>
            ))}
          </select>
        </div>

        <div className="upload-field upload-photo">
          <span id="upload-photo-label">Photo</span>
          <label className="upload-photo-picker" htmlFor="upload-photo">
            <strong>{file ? file.name : 'Tap to choose a photo'}</strong>
            <span>PNG, JPEG, or WebP</span>
            <input
              id="upload-photo"
              type="file"
              accept="image/png,image/jpeg,image/webp"
              aria-labelledby="upload-photo-label"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              required
            />
          </label>
          {previewUrl && (
            <img className="upload-preview" src={previewUrl} alt="Selected clothing preview" />
          )}
        </div>

        <button className="upload-submit" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Uploading…' : 'Add item'}
        </button>

        <p className={statusClass} role="status">
          {status}
        </p>
      </form>
    </main>
  )
}
