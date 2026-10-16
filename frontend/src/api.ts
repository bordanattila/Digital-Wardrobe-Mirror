/**
 * API helpers for talking to the FastAPI backend.
 *
 * In dev, leave VITE_API_BASE_URL empty and use the Vite proxy
 * (see vite.config.ts) so requests stay same-origin.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`API ${path} failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export type HealthResponse = { status: string }

export type ClothingItem = {
  id: number
  name: string
  color: string
  size: string
  category: string
  subcategory: string
  image_path: string
}

export type WeatherConditions = {
  temperature_celsius: number
  temperature_fahrenheit: number
  icon: string
  conditions: string
  city: string | null
}

export type OutfitSuggestions = {
  weather: WeatherConditions
  tops: ClothingItem[]
  bottoms: ClothingItem[]
}

export function getHealth() {
  return apiGet<HealthResponse>('/health')
}

export function getWeather() {
  return apiGet<Record<string, unknown>>('/api/weather/')
}

export function getOutfitSuggestion() {
  return apiGet<OutfitSuggestions>('/api/outfits/suggest')
}

export function listWardrobe() {
  return apiGet<ClothingItem[]>('/api/wardrobe/')
}

export async function createClothingItem(form: FormData): Promise<ClothingItem> {
  const response = await fetch(`${API_BASE}/api/wardrobe/upload`, {
    method: 'POST',
    body: form
  })
  if (!response.ok) {
    throw new Error(`API /api/wardrobe/upload failed: ${response.status}`)
  }
  return response.json() as Promise<ClothingItem>
}

/** URL for <img src> */
export function clothingImageUrl(itemId: number): string {
  return `${API_BASE}/api/wardrobe/${itemId}/image`
}
