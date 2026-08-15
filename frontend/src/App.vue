<script setup>
import { computed, onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import {
  CheckCircle2,
  CircleAlert,
  LoaderCircle,
  Search,
  Sparkles,
  WifiOff,
} from 'lucide-vue-next'

import api, { createResearch } from './services/api'

const status = ref('checking')
const topic = ref('')
const loading = ref(false)
const errorMessage = ref('')
const result = ref(null)

const sampleTopics = [
  'Benefits and limitations of solar energy adoption',
  'How artificial intelligence is changing healthcare',
  'Impact of remote work on employee productivity',
]

const renderedReport = computed(() => {
  if (!result.value?.report) return ''
  return DOMPurify.sanitize(marked.parse(result.value.report))
})

async function checkBackend() {
  status.value = 'checking'

  try {
    const response = await api.get('/api/health')
    status.value = response.data.status === 'healthy' ? 'connected' : 'disconnected'
  } catch (error) {
    console.error(error)
    status.value = 'disconnected'
  }
}

function chooseTopic(value) {
  topic.value = value
  errorMessage.value = ''
}

async function submitResearch() {
  const cleanTopic = topic.value.trim()

  if (cleanTopic.length < 3) {
    errorMessage.value = 'Enter a research topic containing at least 3 characters.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  result.value = null

  try {
    result.value = await createResearch(cleanTopic)
  } catch (error) {
    console.error(error)
    errorMessage.value = error.response?.data?.detail
      || 'The research request failed. Check that FastAPI and LiteLLM are running.'
  } finally {
    loading.value = false
  }
}

onMounted(checkBackend)
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <a class="brand" href="#" aria-label="Research Agent home">
        <span class="brand-icon"><Sparkles :size="20" /></span>
        <span>Research Agent</span>
      </a>

      <div class="connection" :class="status">
        <LoaderCircle v-if="status === 'checking'" :size="16" class="spinner" />
        <CheckCircle2 v-else-if="status === 'connected'" :size="16" />
        <WifiOff v-else :size="16" />
        <span>
          {{ status === 'checking' ? 'Checking backend' : status === 'connected' ? 'Backend connected' : 'Backend offline' }}
        </span>
        <button v-if="status === 'disconnected'" class="retry-link" type="button" @click="checkBackend">
          Retry
        </button>
      </div>
    </header>

    <section class="hero">
      <h1>Turn a question into a<br><span>source-backed report.</span></h1>
      <p>
        Search reliable webpages, compare evidence, and generate a structured research summary with citations.
      </p>

      <form class="research-form" @submit.prevent="submitResearch">
        <label for="topic">What would you like to research?</label>
        <div class="input-row">
          <Search :size="21" class="input-icon" />
          <input
            id="topic"
            v-model="topic"
            type="text"
            maxlength="500"
            placeholder="e.g. Benefits and limitations of renewable energy"
            :disabled="loading"
          >
          <button type="submit" :disabled="loading || status !== 'connected'">
            <LoaderCircle v-if="loading" :size="18" class="spinner" />
            <Search v-else :size="18" />
            {{ loading ? 'Researching…' : 'Research' }}
          </button>
        </div>
        <div class="form-meta">
          <span>Try an example:</span>
          <button
            v-for="sample in sampleTopics"
            :key="sample"
            type="button"
            class="topic-chip"
            :disabled="loading"
            @click="chooseTopic(sample)"
          >
            {{ sample }}
          </button>
        </div>
      </form>
    </section>

    <section v-if="loading" class="state-card loading-card" aria-live="polite">
      <LoaderCircle :size="30" class="spinner" />
      <div>
        <h2>Research in progress</h2>
        <p>Searching sources, reading webpages, and preparing your report. Free models can take a few minutes.</p>
      </div>
    </section>

    <section v-if="errorMessage" class="state-card error-card" role="alert">
      <CircleAlert :size="24" />
      <div>
        <h2>Research could not be completed</h2>
        <p>{{ errorMessage }}</p>
      </div>
    </section>

    <section v-if="result" class="report-card">
      <div class="report-heading">
        <div>
          <span class="report-label">Completed research</span>
          <h2>{{ result.topic }}</h2>
        </div>
        <CheckCircle2 :size="25" />
      </div>
      <article class="markdown-body" v-html="renderedReport" />
    </section>
  </main>
</template>
