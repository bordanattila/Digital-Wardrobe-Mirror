import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { sampleTop } from '../test/fixtures'
import { UploadPage } from './upload_clothing_item'

vi.mock('../api', () => ({
  createClothingItem: vi.fn(),
}))

import { createClothingItem } from '../api'

function renderUpload() {
  return render(
    <MemoryRouter>
      <UploadPage />
    </MemoryRouter>,
  )
}

function fileInput() {
  const input = document.querySelector(
    'input[type="file"]',
  ) as HTMLInputElement | null
  if (!input) throw new Error('file input not found')
  return input
}

async function fillForm(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByPlaceholderText('Name'), 'Summer Tee')
  await user.type(screen.getByPlaceholderText('Color'), 'white')
  await user.type(screen.getByPlaceholderText('Size'), 'M')
  await user.selectOptions(screen.getByLabelText('Category'), 'top')
  await user.type(
    screen.getByPlaceholderText(/e\.g\. t-shirt/),
    't-shirt',
  )
  await user.upload(
    fileInput(),
    new File(['fake-image'], 'tee.png', { type: 'image/png' }),
  )
}

describe('UploadPage', () => {
  beforeEach(() => {
    vi.mocked(createClothingItem).mockReset()
  })

  it('submits FormData with the expected fields', async () => {
    const user = userEvent.setup()
    vi.mocked(createClothingItem).mockResolvedValue(sampleTop)
    const onCreated = vi.fn()

    const { container } = render(
      <MemoryRouter>
        <UploadPage onCreated={onCreated} />
      </MemoryRouter>,
    )
    await fillForm(user)

    const form = container.querySelector('form')
    if (!form) throw new Error('form not found')
    form.noValidate = true

    await user.click(screen.getByRole('button', { name: /Add item/i }))

    await waitFor(() => {
      expect(createClothingItem).toHaveBeenCalledTimes(1)
    })

    const body = vi.mocked(createClothingItem).mock.calls[0][0] as FormData
    expect(body.get('name')).toBe('Summer Tee')
    expect(body.get('color')).toBe('white')
    expect(body.get('size')).toBe('M')
    expect(body.get('category')).toBe('top')
    expect(body.get('subcategory')).toBe('t-shirt')
    expect(body.get('image')).toBeInstanceOf(File)

    expect(await screen.findByText('Created #1: Summer Tee')).toBeInTheDocument()
    expect(onCreated).toHaveBeenCalled()
  })

  it('shows failure status when upload errors', async () => {
    const user = userEvent.setup()
    vi.mocked(createClothingItem).mockRejectedValue(new Error('boom'))

    const { container } = renderUpload()
    await fillForm(user)
    const form = container.querySelector('form')
    if (!form) throw new Error('form not found')
    form.noValidate = true

    await user.click(screen.getByRole('button', { name: /Add item/i }))

    expect(await screen.findByText('Upload failed')).toBeInTheDocument()
  })

  it('asks for an image when none is chosen', async () => {
    const user = userEvent.setup()
    const { container } = renderUpload()

    await user.type(screen.getByPlaceholderText('Name'), 'Summer Tee')
    await user.type(screen.getByPlaceholderText('Color'), 'white')
    await user.type(screen.getByPlaceholderText('Size'), 'M')
    await user.selectOptions(screen.getByLabelText('Category'), 'top')
    await user.type(
      screen.getByPlaceholderText(/e\.g\. t-shirt/),
      't-shirt',
    )

    const form = container.querySelector('form')
    if (!form) throw new Error('form not found')
    form.noValidate = true

    await user.click(screen.getByRole('button', { name: /Add item/i }))

    expect(await screen.findByText('Choose an image')).toBeInTheDocument()
    expect(createClothingItem).not.toHaveBeenCalled()
  })
})
