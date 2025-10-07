import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8080',
})

export async function processDocument(file, extractorMode = 'custom') {
  const form = new FormData()
  form.append('file', file)
  form.append('extractor_mode', extractorMode)

  const { data } = await api.post('/api/v1/documents/process', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

