import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { OutfitSuggestions } from '../api'
import { sampleSuggestion } from '../test/fixtures'
import { MirrorHome } from './mirror'

vi.mock('../api', () => ({
  getOutfitSuggestion: vi.fn(),
  clothingImageUrl: (id: number) => `/api/wardrobe/${id}/image`,
}))

import { getOutfitSuggestion } from '../api'

function renderMirror() {
  return render(
    <MemoryRouter>
      <MirrorHome />
    </MemoryRouter>,
  )
}

describe('MirrorHome', () => {
  beforeEach(() => {
    vi.mocked(getOutfitSuggestion).mockReset()
  })

  it('shows loading inside the mirror shell, then weather and suggestions', async () => {
    vi.mocked(getOutfitSuggestion).mockResolvedValue(sampleSuggestion)
    renderMirror()

    expect(screen.getByText('Loading…')).toBeInTheDocument()
    expect(document.querySelector('.mirror-clock')).toBeInTheDocument()
    expect(document.querySelector('.mirror-page')).toBeInTheDocument()

    expect(await screen.findByRole('heading', { name: 'Weather' })).toBeInTheDocument()
    expect(screen.getByText(/64°F/)).toBeInTheDocument()
    expect(screen.getByText('partly cloudy')).toBeInTheDocument()
    expect(screen.getByText('Testville')).toBeInTheDocument()
    expect(screen.getByText('Summer Tee')).toBeInTheDocument()
    expect(screen.getByText('Blue Jeans')).toBeInTheDocument()
    expect(screen.getByAltText('Summer Tee')).toHaveAttribute(
      'src',
      '/api/wardrobe/1/image',
    )
    expect(
      screen.getByRole('link', { name: /Add clothing \(phone\)/i }),
    ).toHaveAttribute('href', '/upload')
  })

  it('marks the first top and bottom as selected', async () => {
    vi.mocked(getOutfitSuggestion).mockResolvedValue(sampleSuggestion)
    renderMirror()

    await screen.findByText('Summer Tee')

    const topCard = screen.getByText('Summer Tee').closest('article')
    const bottomCard = screen.getByText('Blue Jeans').closest('article')
    expect(topCard).toHaveClass('outfit-card--selected')
    expect(bottomCard).toHaveClass('outfit-card--selected')
  })

  it('shows empty-slot messages when no matches', async () => {
    vi.mocked(getOutfitSuggestion).mockResolvedValue({
      ...sampleSuggestion,
      tops: [],
      bottoms: [],
    })
    renderMirror()

    expect(await screen.findByText('No matching tops')).toBeInTheDocument()
    expect(screen.getByText('No matching bottoms')).toBeInTheDocument()
  })

  it('shows an error inside the shell when the API fails', async () => {
    vi.mocked(getOutfitSuggestion).mockRejectedValue(new Error('network'))
    renderMirror()

    expect(
      await screen.findByText(/Failed to load outfit suggestion/),
    ).toBeInTheDocument()
    expect(document.querySelector('.mirror-clock')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Weather' })).not.toBeInTheDocument()
  })

  it('reloads when Suggest again is clicked', async () => {
    const user = userEvent.setup()
    vi.mocked(getOutfitSuggestion).mockResolvedValue(sampleSuggestion)
    const { container } = renderMirror()

    await screen.findByRole('heading', { name: 'Weather' })
    expect(getOutfitSuggestion).toHaveBeenCalledTimes(1)

    await user.click(
      within(container).getByRole('button', { name: /Suggest again/i }),
    )

    await waitFor(() => {
      expect(getOutfitSuggestion).toHaveBeenCalledTimes(2)
    })
  })

  it('keeps the mirror shell visible while Suggest again reloads', async () => {
    const user = userEvent.setup()
    let resolveReload!: (value: OutfitSuggestions) => void
    const reloadPromise = new Promise<OutfitSuggestions>((resolve) => {
      resolveReload = resolve
    })

    vi.mocked(getOutfitSuggestion)
      .mockResolvedValueOnce(sampleSuggestion)
      .mockReturnValueOnce(reloadPromise)

    renderMirror()
    await screen.findByText('Summer Tee')

    await user.click(screen.getByRole('button', { name: /Suggest again/i }))

    expect(screen.getByText('Loading…')).toBeInTheDocument()
    expect(document.querySelector('.mirror-clock')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Weather' })).not.toBeInTheDocument()

    resolveReload(sampleSuggestion)

    expect(await screen.findByRole('heading', { name: 'Weather' })).toBeInTheDocument()
    expect(screen.queryByText('Loading…')).not.toBeInTheDocument()
  })
})
