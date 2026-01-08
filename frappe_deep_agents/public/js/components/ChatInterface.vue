<template>
  <div class="chat-interface">
    <div class="messages-container" ref="messagesContainer">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['message', msg.role]"
      >
        <div class="message-role">{{ formatRole(msg.role) }}</div>
        <div class="message-content" v-html="renderContent(msg.content)"></div>
        <div v-if="msg.streaming" class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <div v-if="messages.length === 0" class="empty-state">
        <p>Start a conversation with the agent.</p>
      </div>
    </div>

    <div class="input-area">
      <textarea
        v-model="inputText"
        @keydown="handleKeydown"
        placeholder="Type your message... (Shift+Enter for new line)"
        :disabled="isStreaming"
        rows="3"
      ></textarea>
      <button
        class="btn btn-primary"
        @click="send"
        :disabled="!inputText.trim() || isStreaming"
      >
        <span v-if="isStreaming">Processing...</span>
        <span v-else>Send</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

const inputText = ref('')
const messagesContainer = ref(null)

// Auto-scroll on new messages
watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// Also scroll when streaming content updates
watch(
  () => props.messages[props.messages.length - 1]?.content,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  },
  { deep: true }
)

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

function send() {
  if (inputText.value.trim() && !props.isStreaming) {
    emit('send', inputText.value)
    inputText.value = ''
  }
}

function formatRole(role) {
  const roles = {
    user: 'You',
    assistant: 'Agent',
    system: 'System',
    tool: 'Tool'
  }
  return roles[role] || role
}

function renderContent(content) {
  if (!content) return ''

  // Basic markdown rendering
  let html = content
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br>')

  return html
}
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  max-width: 85%;
}

.message.user {
  background: var(--blue-50);
  margin-left: auto;
}

.message.assistant {
  background: var(--gray-100);
  margin-right: auto;
}

.message.system {
  background: var(--yellow-50);
  margin: 0 auto;
  text-align: center;
  font-size: 0.875rem;
}

.message.tool {
  background: var(--purple-50);
  margin-right: auto;
  font-family: monospace;
  font-size: 0.875rem;
}

.message-role {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.message-content {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-content :deep(pre) {
  background: var(--gray-800);
  color: var(--gray-100);
  padding: 0.75rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.message-content :deep(code) {
  background: var(--gray-200);
  padding: 0.125rem 0.25rem;
  border-radius: 2px;
  font-size: 0.875rem;
}

.message-content :deep(pre code) {
  background: none;
  padding: 0;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding-top: 0.5rem;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--gray-400);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.input-area {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background: var(--fg-color);
}

.input-area textarea {
  flex: 1;
  resize: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem;
  font-family: inherit;
  font-size: 0.875rem;
}

.input-area textarea:focus {
  outline: none;
  border-color: var(--primary);
}

.input-area textarea:disabled {
  background: var(--gray-100);
  cursor: not-allowed;
}

.input-area button {
  align-self: flex-end;
  min-width: 80px;
}
</style>
