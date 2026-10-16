import type { ClothingItem, OutfitSuggestions } from '../api'

export const sampleTop: ClothingItem = {
  id: 1,
  name: 'Summer Tee',
  color: 'white',
  size: 'M',
  category: 'top',
  subcategory: 't-shirt',
  image_path: 'tee.png',
}

export const sampleBottom: ClothingItem = {
  id: 2,
  name: 'Blue Jeans',
  color: 'blue',
  size: 'M',
  category: 'bottom',
  subcategory: 'jeans',
  image_path: 'jeans.png',
}

export const sampleSuggestion: OutfitSuggestions = {
  weather: {
    temperature_celsius: 18,
    temperature_fahrenheit: 64,
    icon: '02d',
    conditions: 'partly cloudy',
    city: 'Testville',
  },
  tops: [sampleTop],
  bottoms: [sampleBottom],
}
