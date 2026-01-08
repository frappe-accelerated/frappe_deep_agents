<template>
  <div class="agent-workspace">
    <div class="workspace-header">
      <div class="header-left">
        <h3>{{ agent?.agent_name || 'Agent' }}</h3>
        <span class="session-status" :class="session?.status">
          {{ session?.status || 'Loading...' }}
        </span>
      </div>
      <div class="header-right">
        <button class="btn btn-sm btn-default" @click="newSession">
          New Session
        </button>
        <button class="btn btn-sm btn-default" @click="endSession" v-if="session?.status === 'active'">
          End Session
        </button>
      </div>
    </div>

    <div class="workspace-content">
      <div class="main-panel">
        <ChatInterface
          :messages="messages"
          :is-streaming="isStreaming"
          @send="sendMessage"
        />
      </div>

      <div class="side-panels" v-if="showSidePanels">
        <TodoPanel
          v-if="agent?.enable_todos"
          :todos="todos"
          @update="updateTodo"
        />
        <FilePanel
          v-if="agent?.enable_filesystem"
          :files="files"
          @open="openFile"
          @refresh="refreshFiles"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import ChatInterface from '../components/ChatInterface.vue'
import TodoPanel from '../components/TodoPanel.vue'
import FilePanel from '../components/FilePanel.vue'

const props = defineProps({
  sessionId: String,
  agentName: String
})

const emit = defineEmits(['sessionCreated', 'sessionEnded'])

// State
const session = ref(null)
const agent = ref(null)
const messages = ref([])
const todos = ref([])
const files = ref([])
const isStreaming = ref(false)

// Computed
const showSidePanels = computed(() => {
  return agent.value?.enable_todos || agent.value?.enable_filesystem
})

// Socket connection
let socket = null

onMounted(async () => {
  // Initialize socket
  socket = frappe.socketio.socket

  // Load session if provided
  if (props.sessionId) {
    await loadSession(props.sessionId)
    subscribeToEvents()
  } else if (props.agentName) {
    // Create new session
    await createSession(props.agentName)
  }
})

onUnmounted(() => {
  if (socket && session.value) {
    socket.emit('unsubscribe', `agent_session_${session.value.name}`)
  }
})

async function loadSession(sessionId) {
  try {
    const result = await frappe.call({
      method: 'frappe_deep_agents.api.get_session',
      args: { session_id: sessionId }
    })

    session.value = result.message
    messages.value = result.message.messages || []
    todos.value = result.message.todos || []
    files.value = result.message.files || []

    // Load agent definition
    agent.value = await frappe.db.get_doc('Agent Definition', session.value.agent_definition)
  } catch (error) {
    frappe.msgprint({
      title: 'Error',
      message: error.message || 'Failed to load session',
      indicator: 'red'
    })
  }
}

async function createSession(agentName) {
  try {
    const result = await frappe.call({
      method: 'frappe_deep_agents.api.create_session',
      args: { agent_definition: agentName }
    })

    session.value = { name: result.message.session, status: 'active' }
    agent.value = await frappe.db.get_doc('Agent Definition', agentName)

    subscribeToEvents()
    emit('sessionCreated', session.value.name)
  } catch (error) {
    frappe.msgprint({
      title: 'Error',
      message: error.message || 'Failed to create session',
      indicator: 'red'
    })
  }
}

function subscribeToEvents() {
  if (!socket || !session.value) return

  const channel = `agent_session_${session.value.name}`
  socket.emit('subscribe', channel)

  // Token streaming
  socket.on('agent_token', (data) => {
    if (data.session === session.value.name) {
      appendToken(data.token)
    }
  })

  // Tool results
  socket.on('tool_result', (data) => {
    if (data.session === session.value.name) {
      // Could show tool execution in UI
      console.log('Tool result:', data)
    }
  })

  // Todo updates
  socket.on('todo_update', (data) => {
    if (data.session === session.value.name) {
      todos.value = data.todos
    }
  })

  // File updates
  socket.on('file_update', (data) => {
    if (data.session === session.value.name) {
      files.value = data.files
    }
  })

  // Completion
  socket.on('agent_complete', (data) => {
    if (data.session === session.value.name) {
      isStreaming.value = false
      finishStreaming()
    }
  })

  // Error
  socket.on('agent_error', (data) => {
    if (data.session === session.value.name) {
      isStreaming.value = false
      frappe.msgprint({
        title: 'Agent Error',
        message: data.error,
        indicator: 'red'
      })
    }
  })
}

async function sendMessage(content) {
  if (!content.trim() || isStreaming.value) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: content
  })

  // Add placeholder for assistant response
  messages.value.push({
    role: 'assistant',
    content: '',
    streaming: true
  })

  isStreaming.value = true

  try {
    await frappe.call({
      method: 'frappe_deep_agents.api.send_message',
      args: {
        session_id: session.value.name,
        message: content
      }
    })
  } catch (error) {
    isStreaming.value = false
    frappe.msgprint({
      title: 'Error',
      message: error.message || 'Failed to send message',
      indicator: 'red'
    })
  }
}

function appendToken(token) {
  const lastMsg = messages.value[messages.value.length - 1]
  if (lastMsg && lastMsg.streaming) {
    lastMsg.content += token
  }
}

function finishStreaming() {
  const lastMsg = messages.value[messages.value.length - 1]
  if (lastMsg) {
    lastMsg.streaming = false
  }
}

async function newSession() {
  if (agent.value) {
    await createSession(agent.value.name)
    messages.value = []
    todos.value = []
    files.value = []
  }
}

async function endSession() {
  try {
    await frappe.call({
      method: 'frappe_deep_agents.api.end_session',
      args: { session_id: session.value.name }
    })
    session.value.status = 'completed'
    emit('sessionEnded', session.value.name)
  } catch (error) {
    frappe.msgprint({
      title: 'Error',
      message: error.message || 'Failed to end session',
      indicator: 'red'
    })
  }
}

async function updateTodo(todoName, status) {
  try {
    await frappe.call({
      method: 'frappe_deep_agents.api.update_todo',
      args: { todo_name: todoName, status: status }
    })
  } catch (error) {
    console.error('Failed to update todo:', error)
  }
}

function openFile(file) {
  // Open file in modal or new tab
  frappe.msgprint({
    title: file.file_path,
    message: `<pre>${file.content || 'No content'}</pre>`,
    wide: true
  })
}

async function refreshFiles() {
  // Reload files from session
  if (session.value) {
    const result = await frappe.call({
      method: 'frappe_deep_agents.api.get_session',
      args: { session_id: session.value.name }
    })
    files.value = result.message.files || []
  }
}
</script>

<style scoped>
.agent-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--fg-color);
}

.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h3 {
  margin: 0;
}

.session-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.session-status.active {
  background: var(--green-100);
  color: var(--green-600);
}

.session-status.completed {
  background: var(--gray-100);
  color: var(--gray-600);
}

.session-status.error {
  background: var(--red-100);
  color: var(--red-600);
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

.workspace-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.side-panels {
  width: 300px;
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
