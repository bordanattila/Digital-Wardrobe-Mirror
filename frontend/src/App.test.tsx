import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import App from './App'
import { sampleSuggestion } from './test/fixtures'

vi.mock('./api', () => ({
  getOutfitSuggestion: vi.fn(),
  createClothingItem: vi.fn(),
}))

import { getOutfitSuggestion } from './api'

describe('App routes', () => {
  it('renders MirrorHome on /', async () => {
    vi.mocked(getOutfitSuggestion).mockResolvedValue(sampleSuggestion)

    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('Digital Wardrobe Mirror')).toBeInTheDocument()
    })
  })

  it('renders UploadPage on /upload', () => {
    render(
      <MemoryRouter initialEntries={['/upload']}>
        <App />
      </MemoryRouter>,
    )

    expect(screen.getByText('Add clothing')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Add item/i })).toBeInTheDocument()
  })
})
