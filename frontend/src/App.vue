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

import api, { createFollowUp, createResearch } from './services/api'

const status = ref('checking')
const topic = ref('')
const loading = ref(false)
const errorMessage = ref('')
const result = ref(null)
const followUpQuestion = ref('')
const followUpLoading = ref(false)
const conversation = ref([])

const sampleTopics = [
  'Benefits and limitations of solar energy adoption',
  'How artificial intelligence is changing healthcare',
  'Impact of remote work on employee productivity',
]

const renderedReport = computed(() => {
  if (!result.value?.report) return ''
  return DOMPurify.sanitize(marked.parse(result.value.report))
})

function renderMarkdown(value) {
  return DOMPurify.sanitize(marked.parse(value || ''))
}

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
  conversation.value = []

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

async function submitFollowUp() {
  const question = followUpQuestion.value.trim()
  if (question.length < 3 || !result.value?.session_id) return

  followUpLoading.value = true
  errorMessage.value = ''
  try {
    const response = await createFollowUp(result.value.session_id, question)
    conversation.value.push({
      question: response.question,
      answer: response.answer,
    })
    followUpQuestion.value = ''
  } catch (error) {
    console.error(error)
    errorMessage.value = error.response?.data?.detail
      || 'The follow-up question could not be answered.'
  } finally {
    followUpLoading.value = false
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
      <div class="followup-panel">
        <h3>Continue this research</h3>
        <p>Ask about the existing report or request new information. The agent will decide whether another web search is needed.</p>

        <div v-if="conversation.length" class="conversation">
          <div v-for="(turn, index) in conversation" :key="index" class="conversation-turn">
            <p class="user-question"><strong>You:</strong> {{ turn.question }}</p>
            <div class="markdown-body followup-answer" v-html="renderMarkdown(turn.answer)" />
          </div>
        </div>

        <form class="followup-form" @submit.prevent="submitFollowUp">
          <input
            v-model="followUpQuestion"
            type="text"
            maxlength="1000"
            placeholder="Ask a follow-up question"
            :disabled="followUpLoading"
          >
          <button type="submit" :disabled="followUpLoading || followUpQuestion.trim().length < 3">
            <LoaderCircle v-if="followUpLoading" :size="18" class="spinner" />
            <Search v-else :size="18" />
            {{ followUpLoading ? 'Answering...' : 'Ask follow-up' }}
          </button>
        </form>
      </div>
    </section>
  </main>
</template>
