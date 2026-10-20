import type { ClothingItem, Outfit, OutfitSuggestions } from '../api'

export const sampleTop: ClothingItem = {
  id: 1,
  name: 'Summer Tee',
  color: 'white',
  size: 'M',
  category: 'top',
  subcategory: 't_shirt',
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

export const sampleShoes: ClothingItem = {
  id: 3,
  name: 'White Sneakers',
  color: 'white',
  size: 'M',
  category: 'shoes',
  subcategory: 'sneakers',
  image_path: 'sneakers.png',
}

export const sampleOutfit: Outfit = {
  top: [sampleTop],
  bottom: [sampleBottom],
  shoes: [sampleShoes],
  mid_layer: [],
  outer_layer: [],
  score: 0,
  reason: 'Mild — light mid layer',
}

export const sampleSuggestion: OutfitSuggestions = {
  weather: {
    temperature_celsius: 18,
    temperature_fahrenheit: 64,
    icon: '02d',
    conditions: 'partly cloudy',
    city: 'Testville',
  },
  outfits: [sampleOutfit],
}
