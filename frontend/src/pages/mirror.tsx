import { useEffect, useState, type CSSProperties } from 'react'
import { Link } from 'react-router-dom'
import { clothingImageUrl, getOutfitSuggestion, type OutfitSuggestions } from '../api'
import './mirror.css'


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

  // Clock: update every minute
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
  const tops = suggestion?.tops ?? []
  const bottoms = suggestion?.bottoms ?? []

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
                {weather.temperature_fahrenheit}°F {' '}
                <img src={`https://openweathermap.org/img/wn/${weather.icon}.png`} alt={weather.icon} />
              </p>
              <p>{weather.conditions}</p>
              <p>{weather.city ?? 'Local'}</p>
            </section>
            <section className="mirror-panel">
              <h2>Today's Outfit Suggestions</h2>
              <h3>Suggested tops</h3>
              {tops.length === 0 ? (
                <p>No matching tops</p>
              ) : (
                <div className="outfit-row">
                  {tops.map((item, index) => {
                    const imageUrl = clothingImageUrl(item.id)
                    const selected = index === 0
                    return (
                      <article
                        key={item.id}
                        className={
                          selected ? 'outfit-card outfit-card--selected' : 'outfit-card'
                        }
                        style={
                          selected
                            ? ({
                              '--outfit-card-image': `url(${imageUrl})`,
                            } as CSSProperties)
                            : undefined
                        }
                      >
                        <img src={imageUrl} alt={item.name} />
                        <div>{item.name}</div>
                      </article>
                    )
                  })}
                </div>
              )}
            </section>
            <section className="mirror-panel">
              <h3>Suggested bottoms</h3>
              {bottoms.length === 0 ? (
                <p>No matching bottoms</p>
              ) : (
                <div className="outfit-row">
                  {bottoms.map((item, index) => {
                    const imageUrl = clothingImageUrl(item.id)
                    const selected = index === 0
                    return (
                      <article
                        key={item.id}
                        className={
                          selected ? 'outfit-card outfit-card--selected' : 'outfit-card'
                        }
                        style={
                          selected
                            ? ({
                              '--outfit-card-image': `url(${imageUrl})`,
                            } as CSSProperties)
                            : undefined
                        }
                      >
                        <img src={imageUrl} alt={item.name} />
                        <div>{item.name}</div>
                      </article>
                    )
                  })}
                </div>
              )}
            </section>
          </>
        )}
        <button type="button" onClick={loadSuggestion}>Suggest again</button>
        <Link to="/upload">Add clothing (phone)</Link>
      </aside>
    </div>
  )
}