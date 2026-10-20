import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  clothingImageUrl,
  getOutfitSuggestion,
  type ClothingItem,
  type Outfit,
  type OutfitSuggestions,
} from '../api'
import './mirror.css'

const SLOT_ORDER = [
  'outer_layer',
  'mid_layer',
  'top',
  'bottom',
  'shoes',
] as const

type SlotKey = (typeof SLOT_ORDER)[number]

function piecesForOutfit(outfit: Outfit): { slot: SlotKey; item: ClothingItem }[] {
  const pieces: { slot: SlotKey; item: ClothingItem }[] = []
  for (const slot of SLOT_ORDER) {
    for (const item of outfit[slot]) {
      pieces.push({ slot, item })
    }
  }
  return pieces
}

function slotLabel(slot: SlotKey): string {
  return slot.replaceAll('_', ' ')
}

export function MirrorHome() {
  const [suggestion, setSuggestion] = useState<OutfitSuggestions | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  function loadSuggestion() {
    setIsLoading(true)
    setError(null)
    getOutfitSuggestion()
      .then((data: OutfitSuggestions) => setSuggestion(data))
      .catch(() => setError('Failed to load outfit suggestion.'))
      .finally(() => setIsLoading(false))
  }

  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])
  const timeLabel = now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
  const dateLabel = now.toLocaleDateString([], {
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
  })

  useEffect(() => {
    loadSuggestion()
  }, [])

  const weather = suggestion?.weather
  const outfits = suggestion?.outfits ?? []

  return (
    <div className="mirror-page">
      <div className="mirror-reflection" aria-hidden="true" />
      <aside className="mirror-ui">
        <header className="mirror-panel">
          <div className="mirror-clock">{timeLabel}</div>
          <div className="mirror-date">{dateLabel}</div>
        </header>

        {isLoading && <p>Loading…</p>}
        {error && <p>{error}</p>}

        {!isLoading && !error && weather && (
          <>
            <section className="mirror-panel">
              <h2>Weather</h2>
              <p style={{ fontSize: '2rem', margin: 0 }}>
                {weather.temperature_fahrenheit}°F{' '}
                <img
                  src={`https://openweathermap.org/img/wn/${weather.icon}.png`}
                  alt={weather.icon}
                />
              </p>
              <p>{weather.conditions}</p>
              <p>{weather.city ?? 'Local'}</p>
            </section>

            <section className="mirror-panel">
              <h2>Today&apos;s Outfit Suggestions</h2>
              {outfits.length === 0 ? (
                <p>No matching outfits for this weather.</p>
              ) : (
                <div className="look-list">
                  {outfits.map((outfit, index) => {
                    const pieces = piecesForOutfit(outfit)
                    const selected = index === 0

                    return (
                      <article
                        key={`look-${index}-${outfit.top[0]?.id ?? index}`}
                        className={
                          selected ? 'look-card look-card--selected' : 'look-card'
                        }
                      >
                        <p className="look-reason">{outfit.reason}</p>
                        <div className="look-pieces">
                          {pieces.map(({ slot, item }) => (
                            <div key={`${slot}-${item.id}`} className="look-piece">
                              <img
                                src={clothingImageUrl(item.id)}
                                alt={item.name}
                              />
                              <div className="look-piece-slot">{slotLabel(slot)}</div>
                              <div className="look-piece-name">{item.name}</div>
                            </div>
                          ))}
                        </div>
                      </article>
                    )
                  })}
                </div>
              )}
            </section>
          </>
        )}

        <button type="button" onClick={loadSuggestion}>
          Suggest again
        </button>
        <Link to="/upload">Add clothing (phone)</Link>
      </aside>
    </div>
  )
}
