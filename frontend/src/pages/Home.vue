<template>
	<div class="home-page h-full flex">
		<!-- Sidebar with session list -->
		<aside class="w-80 border-r bg-white flex flex-col">
			<div class="p-4 border-b">
				<h2 class="text-lg font-semibold text-gray-900">Deep Agents</h2>
			</div>

			<div class="p-4">
				<Button variant="solid" @click="showNewSession = true" class="w-full">
					<template #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
						</svg>
					</template>
					New Session
				</Button>
			</div>

			<!-- Session list -->
			<div class="session-list flex-1 overflow-y-auto">
				<div v-if="loading" class="p-4 text-center text-gray-500">
					Loading sessions...
				</div>
				<div v-else-if="sessions.length === 0" class="p-4 text-center text-gray-500">
					No sessions yet. Create one to get started!
				</div>
				<div
					v-for="session in sessions"
					:key="session.name"
					@click="openSession(session.name)"
					class="session-item p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors"
					:class="{ 'bg-blue-50': activeSession === session.name }"
				>
					<div class="flex justify-between items-start">
						<div class="flex-1 min-w-0">
							<div class="font-medium text-sm text-gray-900 truncate">
								{{ session.agent_definition }}
							</div>
							<div class="text-xs text-gray-500 mt-1">
								{{ formatDate(session.creation) }}
							</div>
						</div>
						<Badge :label="session.status" :theme="getStatusTheme(session.status)" />
					</div>
				</div>
			</div>
		</aside>

		<!-- Main content area -->
		<main class="flex-1 flex items-center justify-center bg-gray-50">
			<div class="text-center max-w-md px-4">
				<div class="text-6xl mb-6">🤖</div>
				<h1 class="text-3xl font-bold mb-3 text-gray-900">Frappe Deep Agents</h1>
				<p class="text-gray-600 mb-8 text-lg">
					Create intelligent agents with LangChain and Kubernetes sandboxes
				</p>
				<Button variant="solid" size="lg" @click="showNewSession = true">
					<template #prefix>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
						</svg>
					</template>
					Start New Session
				</Button>
			</div>
		</main>

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

					<div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
						<p class="text-sm text-red-800">{{ error }}</p>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, Dialog } from 'frappe-ui'
import { agentAPI } from '../utils/api'
import { formatDate, getStatusTheme } from '../utils/helpers'

const router = useRouter()

// State
const sessions = ref([])
const agents = ref([])
const loading = ref(false)
const showNewSession = ref(false)
const selectedAgent = ref('')
const creating = ref(false)
const error = ref('')
const activeSession = ref(null)

// Computed
const selectedAgentData = computed(() => {
	if (!selectedAgent.value) return null
	return agents.value.find(a => a.name === selectedAgent.value)
})

// Methods
async function loadSessions() {
	loading.value = true
	try {
		sessions.value = await agentAPI.listSessions()
		// Sort by creation date, newest first
		sessions.value.sort((a, b) => new Date(b.creation) - new Date(a.creation))
	} catch (err) {
		console.error('Failed to load sessions:', err)
	} finally {
		loading.value = false
	}
}

async function loadAgents() {
	try {
		agents.value = await agentAPI.listAgents()
	} catch (err) {
		console.error('Failed to load agents:', err)
	}
}

async function createSession() {
	if (!selectedAgent.value) return

	creating.value = true
	error.value = ''

	try {
		const session = await agentAPI.createSession(selectedAgent.value)
		showNewSession.value = false
		selectedAgent.value = ''

		// Refresh sessions list
		await loadSessions()

		// Navigate to workspace
		router.push(`/agent/workspace/${session.name}`)
	} catch (err) {
		error.value = err.message || 'Failed to create session'
		console.error('Failed to create session:', err)
	} finally {
		creating.value = false
	}
}

function openSession(sessionId) {
	activeSession.value = sessionId
	router.push(`/agent/workspace/${sessionId}`)
}

// Lifecycle
onMounted(() => {
	loadSessions()
	loadAgents()
})
</script>
