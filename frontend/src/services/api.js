import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 250000,
})

export async function createResearch(topic) {
  const response = await api.post('/api/research', {
    topic,
  })

  return response.data
}

export default api
