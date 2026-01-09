<template>
  <div
    :class="[
      'message-wrapper flex',
      message.role === 'user' ? 'justify-end' : 'justify-start'
    ]"
  >
    <div
      :class="[
        'message max-w-2xl rounded-2xl px-4 py-3 shadow-sm',
        messageClass
      ]"
    >
      <div class="message-role text-xs font-semibold mb-1 opacity-75">
        {{ formatRole(message.role) }}
      </div>
      <div class="prose prose-sm max-w-none" v-html="renderedContent"></div>
      <div v-if="message.streaming" class="typing-indicator mt-2">
        <span></span><span></span><span></span>
      </div>
      <div v-if="message.timestamp" class="text-xs opacity-50 mt-2">
        {{ formatTime(message.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import 'highlight.js/styles/github.css'

// Register highlight.js languages
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('json', json)

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

// Configure marked for syntax highlighting
marked.setOptions({
  breaks: true,
  gfm: true,
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight error:', err)
      }
    }
    return code
  }
})

const renderedContent = computed(() => {
  if (!props.message.content) return ''

  try {
    return marked.parse(props.message.content)
  } catch (err) {
    console.error('Markdown parse error:', err)
    return props.message.content.replace(/\n/g, '<br>')
  }
})

const messageClass = computed(() => {
  const role = props.message.role
  return {
    'bg-blue-500 text-white': role === 'user',
    'bg-gray-100 text-gray-900': role === 'assistant',
    'bg-yellow-50 text-yellow-900 border border-yellow-200': role === 'system',
    'bg-purple-50 text-purple-900 border border-purple-200': role === 'tool'
  }
})

const formatRole = (role) => {
  const roles = {
    user: 'You',
    assistant: 'Agent',
    system: 'System',
    tool: 'Tool'
  }
  return roles[role] || role
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* User messages stay on right with blue background */
.message.user .prose {
  color: white;
}

.message.user .prose code {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Assistant messages have white/gray prose styling */
.message.assistant .prose {
  color: #1f2937;
}
</style>
