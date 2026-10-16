import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  createClothingItem,
  getHealth,
  getOutfitSuggestion,
  listWardrobe,
} from './api'
import { sampleSuggestion, sampleTop } from './test/fixtures'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

function mockFetchOk(data: unknown, status = 200) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: async () => data,
    }),
  )
}

describe('api helpers', () => {
  it('getHealth requests /health', async () => {
    mockFetchOk({ status: 'healthy' })
    await expect(getHealth()).resolves.toEqual({ status: 'healthy' })
    expect(fetch).toHaveBeenCalledWith('/health')
  })

  it('getOutfitSuggestion requests suggest endpoint', async () => {
    mockFetchOk(sampleSuggestion)
    await expect(getOutfitSuggestion()).resolves.toEqual(sampleSuggestion)
    expect(fetch).toHaveBeenCalledWith('/api/outfits/suggest')
  })

  it('listWardrobe requests wardrobe list', async () => {
    mockFetchOk([sampleTop])
    await expect(listWardrobe()).resolves.toEqual([sampleTop])
    expect(fetch).toHaveBeenCalledWith('/api/wardrobe/')
  })

  it('createClothingItem posts FormData to upload', async () => {
    mockFetchOk(sampleTop)
    const form = new FormData()
    form.append('name', 'Summer Tee')
    await expect(createClothingItem(form)).resolves.toEqual(sampleTop)
    expect(fetch).toHaveBeenCalledWith(
      '/api/wardrobe/upload',
      expect.objectContaining({ method: 'POST', body: form }),
    )
  })

  it('throws when response is not ok', async () => {
    mockFetchOk({ detail: 'fail' }, 502)
    await expect(getOutfitSuggestion()).rejects.toThrow(
      'API /api/outfits/suggest failed: 502',
    )
  })
})
