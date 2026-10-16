import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  listWardrobe,
  deleteClothingItem,
  clothingImageUrl,
  type ClothingItem,
} from '../api'
import './full_wardrobe.css'

export function FullWardrobe() {
  const [wardrobe, setWardrobe] = useState<ClothingItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  function loadWardrobe() {
    setIsLoading(true)
    setError(null)
    listWardrobe()
      .then(setWardrobe)
      .catch(() => setError('Failed to load wardrobe.'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    loadWardrobe()
  }, [])

  async function handleDelete(item: ClothingItem) {
    const ok = window.confirm(`Delete “${item.name}”? This cannot be undone.`)
    if (!ok) return

    try {
      setDeletingId(item.id)
      setError(null)
      await deleteClothingItem(item.id)
      setWardrobe((items) => items.filter((entry) => entry.id !== item.id))
    } catch {
      setError(`Failed to delete “${item.name}”.`)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="wardrobe-page">
      <nav className="wardrobe-nav">
        <Link to="/">Mirror</Link>
        <Link to="/upload">Add clothing</Link>
      </nav>

      <header className="wardrobe-header">
        <div>
          <h1>Full wardrobe</h1>
          <p>Everything in inventory — review, then remove what you no longer wear.</p>
        </div>
        {!isLoading && !error && (
          <div className="wardrobe-count">
            {wardrobe.length} item{wardrobe.length === 1 ? '' : 's'}
          </div>
        )}
      </header>

      {isLoading && <p className="wardrobe-status">Loading…</p>}
      {error && <p className="wardrobe-status wardrobe-status--error">{error}</p>}

      {!isLoading && !error && wardrobe.length === 0 && (
        <div className="wardrobe-empty">
          <p>No clothing items in wardrobe.</p>
          <p>
            <Link to="/upload">Add your first piece</Link>
          </p>
        </div>
      )}

      {!isLoading && !error && wardrobe.length > 0 && (
        <ul className="wardrobe-grid">
          {wardrobe.map((item) => (
            <li key={item.id} className="wardrobe-card">
              <img
                src={clothingImageUrl(item.id)}
                alt={item.name}
              />
              <div className="wardrobe-card-name">{item.name}</div>
              <p className="wardrobe-card-meta">
                {item.color} · {item.size}
                <br />
                {item.category} / {item.subcategory}
              </p>
              <button
                type="button"
                className="wardrobe-card-delete"
                disabled={deletingId === item.id}
                onClick={() => handleDelete(item)}
              >
                {deletingId === item.id ? 'Deleting…' : 'Delete'}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
