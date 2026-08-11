<script setup>
import { onMounted, ref } from 'vue'
import {
  CheckCircle,
  LoaderCircle,
  WifiOff,
} from 'lucide-vue-next'

import api from './services/api'

const status = ref('checking')
const message = ref('Checking backend connection...')

async function checkBackend() {
  status.value = 'checking'
  message.value = 'Checking backend connection...'

  try {
    const response = await api.get('/api/health')

    if (response.data.status !== 'healthy') {
      throw new Error('Unexpected health response')
    }

    status.value = 'connected'
    message.value = 'FastAPI backend is connected.'
  } catch (error) {
    console.error(error)
    status.value = 'disconnected'
    message.value = 'Could not connect to the FastAPI backend.'
  }
}

onMounted(checkBackend)
</script>

<template>
  <main class="page">
    <section class="card">
      <h1>Research Agent</h1>

      <p class="description">
        Vue frontend with FastAPI backend
      </p>

      <div class="status" :class="status">
        <LoaderCircle
          v-if="status === 'checking'"
          :size="22"
          class="spinner"
        />

        <CheckCircle
          v-else-if="status === 'connected'"
          :size="22"
        />

        <WifiOff
          v-else
          :size="22"
        />

        <span>{{ message }}</span>
      </div>

      <button
        v-if="status === 'disconnected'"
        type="button"
        @click="checkBackend"
      >
        Try again
      </button>
    </section>
  </main>
</template>



