<template>
	<div class="agent-workspace h-screen flex flex-col overflow-hidden bg-gray-50">
		<!-- Frappe UI Header Bar -->
		<header class="h-12 bg-white border-b border-gray-200 flex items-center px-4 flex-shrink-0">
			<div class="flex items-center space-x-4">
				<!-- Sidebar toggle -->
				<button
					@click="sidebarCollapsed = !sidebarCollapsed"
					class="p-1.5 rounded hover:bg-gray-100 transition-colors text-gray-600"
					:title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
				>
					<svg v-if="!sidebarCollapsed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
					</svg>
					<svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
					</svg>
				</button>

				<!-- App branding -->
				<div class="flex items-center space-x-2">
					<div class="text-lg font-semibold text-gray-900">Deep Agents</div>
				</div>
			</div>

			<!-- Center: Session info -->
			<div class="flex-1 flex justify-center">
				<div v-if="session" class="flex items-center space-x-2 text-sm">
					<span class="text-gray-600">{{ session.agent_definition }}</span>
					<span class="text-gray-400">|</span>
					<Badge :label="session.status || 'Active'" :theme="getStatusTheme(session.status)" />
				</div>
			</div>

			<!-- Right: User menu placeholder -->
			<div class="flex items-center space-x-2">
				<Button variant="ghost" size="sm" @click="goToDesk">
					Desk
				</Button>
			</div>
		</header>

		<!-- Main content area -->
		<div class="flex flex-1 overflow-hidden">
			<!-- Left: Session Sidebar -->
			<transition name="slide">
				<SessionSidebar
					v-if="!sidebarCollapsed"
					:sessions="sessions"
					:current-session="session"
					@new-session="handleNewSession"
					@select-session="handleSelectSession"
				/>
			</transition>

			<!-- Center: Chat Interface -->
			<div class="flex-1 flex flex-col min-w-0 bg-white">
				<ChatInterface
					:messages="messages"
					:is-streaming="isStreaming"
					@send="sendMessage"
				/>
			</div>

			<!-- Right: Activity Sidebar -->
			<ActivitySidebar
				:tool-calls="toolCalls"
				:files="files"
				:todos="todos"
				:agent-status="agentStatus"
				@preview-file="handleFilePreview"
			/>
		</div>

		<!-- File Preview Dialog -->
		<Dialog v-model="showFileViewer" :options="{ title: currentFile?.file_path || 'File', size: '4xl' }">
			<template #body-content>
				<div v-if="currentFile" class="file-viewer">
					<pre class="bg-gray-50 p-4 rounded-lg overflow-x-auto max-h-96 text-sm"><code>{{ fileContent || 'Loading...' }}</code></pre>
				</div>
			</template>
		</Dialog>

		<!-- New Session Dialog -->
		<Dialog v-model="showNewSession" :options="{ title: 'New Agent Session', size: 'lg' }">
			<template #body-content>
				<div class="space-y-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Select Agent</label>
						<select
							v-model="selectedAgent"
							class="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">Choose an agent...</option>
							<option v-for="agent in agents" :key="agent.name" :value="agent.name">
								{{ agent.agent_name }}
							</option>
						</select>
						<p v-if="selectedAgentData" class="text-sm text-gray-600 mt-2">
							{{ selectedAgentData.description || 'No description available' }}
						</p>
					</div>
				</div>
			</template>
			<template #actions>
				<Button variant="subtle" @click="showNewSession = false">Cancel</Button>
				<Button
					variant="solid"
					@click="createSession"
					:disabled="!selectedAgent || creating"
					:loading="creating"
				>
					{{ creating ? 'Creating...' : 'Create Session' }}
				</Button>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, Button, Badge } from 'frappe-ui'
import SessionSidebar from '../components/SessionSidebar.vue'
import ChatInterface from '../components/ChatInterface.vue'
import ActivitySidebar from '../components/ActivitySidebar.vue'
import socketService from '../socket'
import { agentAPI } from '../utils/api'

const props = defineProps({
	sessionId: String
})

const router = useRouter()

// State
const session = ref(null)
const sessions = ref([])
const agents = ref([])
const messages = ref([])
const todos = ref([])
const files = ref([])
const toolCalls = ref([])
const isStreaming = ref(false)
const agentStatus = ref('idle')
const showFileViewer = ref(false)
const currentFile = ref(null)
const fileContent = ref('')
const loading = ref(false)
const sidebarCollapsed = ref(false)

// New session dialog
const showNewSession = ref(false)
const selectedAgent = ref('')
const creating = ref(false)

const selectedAgentData = computed(() => {
	if (!selectedAgent.value) return null
	return agents.value.find(a => a.name === selectedAgent.value)
})

// Status theme helper
const getStatusTheme = (status) => {
	const themes = {
		'active': 'green',
		'Active': 'green',
		'completed': 'blue',
		'error': 'red',
		'timeout': 'orange'
	}
	return themes[status] || 'gray'
}

// Navigate to desk
const goToDesk = () => {
	window.location.href = '/app'
}

// Socket connection
onMounted(async () => {
	// Load all sessions and agents
	await Promise.all([loadSessions(), loadAgents()])

	// Load specific session if provided
	if (props.sessionId) {
		await loadSession(props.sessionId)
		subscribeToEvents()
	}
})

onUnmounted(() => {
	if (session.value) {
		const channel = `agent_session_${session.value.name}`
		socketService.unsubscribe(channel)
	}
})

async function loadSessions() {
	try {
		const result = await agentAPI.listSessions()
		sessions.value = result || []
		// Sort by creation date, newest first
		sessions.value.sort((a, b) => new Date(b.creation) - new Date(a.creation))
	} catch (error) {
		console.error('Failed to load sessions:', error)
		sessions.value = []
	}
}

async function loadAgents() {
	try {
		agents.value = await agentAPI.listAgents()
	} catch (error) {
		console.error('Failed to load agents:', error)
		agents.value = []
	}
}

async function loadSession(sessionId) {
	loading.value = true
	try {
		const result = await agentAPI.getSession(sessionId)

		session.value = result
		messages.value = result.messages || []
		todos.value = result.todos || []
		files.value = result.files || []
		toolCalls.value = result.tool_calls || []

		agentStatus.value = result.status === 'active' ? 'idle' : result.status
	} catch (error) {
		console.error('Failed to load session:', error)
		agentStatus.value = 'error'
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
			agentStatus.value = 'streaming'
			appendToken(data.token)
		}
	})

	// Tool call start
	socketService.on('tool_call_start', (data) => {
		if (data.session === session.value.name) {
			agentStatus.value = 'running'
			toolCalls.value.push({
				id: Date.now().toString(),
				tool_name: data.tool_name,
				input: data.input,
				status: 'running',
				timestamp: new Date()
			})
		}
	})

	// Tool call complete
	socketService.on('tool_call_complete', (data) => {
		if (data.session === session.value.name) {
			const tool = toolCalls.value.find(t => t.tool_name === data.tool_name && t.status === 'running')
			if (tool) {
				tool.status = data.success ? 'success' : 'error'
				tool.output = data.output
			}
		}
	})

	// Agent status updates
	socketService.on('agent_status', (data) => {
		if (data.session === session.value.name) {
			agentStatus.value = data.status
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
			agentStatus.value = 'completed'
			finishStreaming()
		}
	})

	// Error
	socketService.on('agent_error', (data) => {
		if (data.session === session.value.name) {
			isStreaming.value = false
			agentStatus.value = 'error'
			console.error('Agent error:', data.error)
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
		content: content,
		timestamp: new Date()
	})

	// Add placeholder for assistant response
	messages.value.push({
		role: 'assistant',
		content: '',
		streaming: true
	})

	isStreaming.value = true
	agentStatus.value = 'thinking'

	try {
		await agentAPI.sendMessage(session.value.name, content)
	} catch (error) {
		isStreaming.value = false
		agentStatus.value = 'error'
		console.error('Failed to send message:', error)
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
		lastMsg.timestamp = new Date()
	}
}

async function handleNewSession() {
	showNewSession.value = true
}

async function createSession() {
	if (!selectedAgent.value) return

	creating.value = true

	try {
		const result = await agentAPI.createSession(selectedAgent.value)

		showNewSession.value = false
		selectedAgent.value = ''

		// Unsubscribe from current session
		if (session.value) {
			const channel = `agent_session_${session.value.name}`
			socketService.unsubscribe(channel)
		}

		// Navigate to new session
		router.push(`/agent/workspace/${result.name}`)

		// Reload sessions list and load the new session
		await loadSessions()
		await loadSession(result.name)
		subscribeToEvents()
	} catch (error) {
		console.error('Failed to create session:', error)
	} finally {
		creating.value = false
	}
}

async function handleSelectSession(sessionId) {
	// Unsubscribe from current session
	if (session.value) {
		const channel = `agent_session_${session.value.name}`
		socketService.unsubscribe(channel)
	}

	// Clear current state
	messages.value = []
	toolCalls.value = []
	files.value = []
	todos.value = []

	// Navigate to selected session
	router.push(`/agent/workspace/${sessionId}`)

	// Load the session
	await loadSession(sessionId)
	subscribeToEvents()
}

async function handleFilePreview(file) {
	currentFile.value = file
	showFileViewer.value = true
	fileContent.value = 'Loading...'

	try {
		const content = await agentAPI.getFileContent(file.name)
		fileContent.value = content || 'No content'
	} catch (error) {
		fileContent.value = file.content || 'Failed to load file content'
		console.error('Failed to load file:', error)
	}
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
	transition: all 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
	margin-left: -250px;
	opacity: 0;
}
</style>
