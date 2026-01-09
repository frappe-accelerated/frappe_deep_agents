<template>
	<div class="agent-workspace flex flex-col h-full bg-white">
		<!-- Header -->
		<div class="workspace-header flex justify-between items-center px-4 py-3 border-b">
			<div class="header-left flex items-center gap-4">
				<h3 class="m-0 text-lg font-semibold">{{ agent?.agent_name || 'Agent' }}</h3>
				<Badge
					v-if="session?.status"
					:label="session.status.toUpperCase()"
					:theme="getStatusTheme(session.status)"
				/>
			</div>
			<div class="header-right flex gap-2">
				<Button variant="subtle" size="sm" @click="newSession">
					New Session
				</Button>
				<Button
					v-if="session?.status === 'Active'"
					variant="subtle"
					size="sm"
					@click="endSession"
				>
					End Session
				</Button>
			</div>
		</div>

		<!-- Content -->
		<div class="workspace-content flex flex-1 overflow-hidden">
			<!-- Main chat panel -->
			<div class="main-panel flex-1 flex flex-col overflow-hidden">
				<ChatInterface
					:messages="messages"
					:is-streaming="isStreaming"
					@send="sendMessage"
				/>
			</div>

			<!-- Side panels (todos & files) -->
			<div
				v-if="showSidePanels"
				class="side-panels w-80 border-l flex flex-col overflow-hidden"
			>
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

		<!-- File viewer dialog -->
		<Dialog v-model="showFileViewer" :options="{ title: currentFile?.file_path || 'File', size: '4xl' }">
			<template #body-content>
				<div v-if="currentFile" class="file-viewer">
					<pre class="bg-gray-50 p-4 rounded-lg overflow-x-auto max-h-96"><code>{{ fileContent || 'Loading...' }}</code></pre>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, Dialog } from 'frappe-ui'
import ChatInterface from '../components/ChatInterface.vue'
import TodoPanel from '../components/TodoPanel.vue'
import FilePanel from '../components/FilePanel.vue'
import socketService from '../socket'
import { agentAPI } from '../utils/api'
import { getStatusTheme } from '../utils/helpers'

const props = defineProps({
	sessionId: String
})

const router = useRouter()

// State
const session = ref(null)
const agent = ref(null)
const messages = ref([])
const todos = ref([])
const files = ref([])
const isStreaming = ref(false)
const showFileViewer = ref(false)
const currentFile = ref(null)
const fileContent = ref('')
const loading = ref(false)

// Computed
const showSidePanels = computed(() => {
	return agent.value?.enable_todos || agent.value?.enable_filesystem
})

// Socket connection
onMounted(async () => {
	// Load session
	if (props.sessionId) {
		await loadSession(props.sessionId)
		subscribeToEvents()
	} else {
		// No session ID, go back to home
		router.push('/agent')
	}
})

onUnmounted(() => {
	if (session.value) {
		const channel = `agent_session_${session.value.name}`
		socketService.unsubscribe(channel)
	}
})

async function loadSession(sessionId) {
	loading.value = true
	try {
		const result = await agentAPI.getSession(sessionId)

		session.value = result
		messages.value = result.messages || []
		todos.value = result.todos || []
		files.value = result.files || []

		// Get agent definition details
		agent.value = {
			name: result.agent_definition,
			agent_name: result.agent_definition,
			enable_todos: true, // Assume enabled for now
			enable_filesystem: true
		}
	} catch (error) {
		console.error('Failed to load session:', error)
		// Navigate back to home on error
		router.push('/agent')
	} finally {
		loading.value = false
	}
}

function subscribeToEvents() {
	if (!session.value) return

	const channel = `agent_session_${session.value.name}`
	socketService.subscribe(channel)

	// Token streaming
	socketService.on('agent_token', (data) => {
		if (data.session === session.value.name) {
			appendToken(data.token)
		}
	})

	// Tool results
	socketService.on('tool_result', (data) => {
		if (data.session === session.value.name) {
			console.log('Tool result:', data)
			// Optionally show in chat
		}
	})

	// Todo updates
	socketService.on('todo_update', (data) => {
		if (data.session === session.value.name) {
			todos.value = data.todos
		}
	})

	// File updates
	socketService.on('file_update', (data) => {
		if (data.session === session.value.name) {
			files.value = data.files
		}
	})

	// Completion
	socketService.on('agent_complete', (data) => {
		if (data.session === session.value.name) {
			isStreaming.value = false
			finishStreaming()
		}
	})

	// Error
	socketService.on('agent_error', (data) => {
		if (data.session === session.value.name) {
			isStreaming.value = false
			console.error('Agent error:', data.error)
			// Show error message in chat
			messages.value.push({
				role: 'system',
				content: `Error: ${data.error}`
			})
		}
	})
}

async function sendMessage(content) {
	if (!content.trim() || isStreaming.value || !session.value) return

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
		await agentAPI.sendMessage(session.value.name, content)
	} catch (error) {
		isStreaming.value = false
		console.error('Failed to send message:', error)
		// Show error
		messages.value.push({
			role: 'system',
			content: `Error: ${error.message || 'Failed to send message'}`
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
	if (!agent.value) return

	try {
		const result = await agentAPI.createSession(agent.value.name)
		// Navigate to new session
		router.push(`/agent/workspace/${result.name}`)
		// Reload
		await loadSession(result.name)
		subscribeToEvents()
	} catch (error) {
		console.error('Failed to create session:', error)
	}
}

async function endSession() {
	if (!session.value) return

	try {
		await agentAPI.endSession(session.value.name)
		session.value.status = 'Ended'
	} catch (error) {
		console.error('Failed to end session:', error)
	}
}

async function updateTodo(todoName, status) {
	try {
		await agentAPI.updateTodo(todoName, status)
		// Update local state
		const todo = todos.value.find(t => t.name === todoName)
		if (todo) {
			todo.status = status
		}
	} catch (error) {
		console.error('Failed to update todo:', error)
	}
}

async function openFile(file) {
	currentFile.value = file
	showFileViewer.value = true
	fileContent.value = 'Loading...'

	try {
		const content = await agentAPI.getFileContent(file.name)
		fileContent.value = content || 'No content'
	} catch (error) {
		fileContent.value = 'Failed to load file content'
		console.error('Failed to load file:', error)
	}
}

async function refreshFiles() {
	if (!session.value) return

	try {
		const result = await agentAPI.getSession(session.value.name)
		files.value = result.files || []
	} catch (error) {
		console.error('Failed to refresh files:', error)
	}
}
</script>
