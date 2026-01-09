<template>
	<div class="session-sidebar flex flex-col h-full bg-gray-50 border-r border-gray-200">
		<!-- Header with New Chat button -->
		<div class="p-3 border-b border-gray-200">
			<Button
				variant="solid"
				@click="$emit('new-session')"
				class="w-full"
			>
				<template #prefix>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
				</template>
				New Chat
			</Button>
		</div>

		<!-- Search bar -->
		<div class="p-3 border-b border-gray-200">
			<div class="relative">
				<svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
				</svg>
				<input
					v-model="searchQuery"
					placeholder="Search sessions..."
					class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
				/>
			</div>
		</div>

		<!-- Session list -->
		<div class="flex-1 overflow-y-auto">
			<div v-if="filteredSessions.length === 0" class="p-4 text-center text-gray-500 text-sm">
				{{ searchQuery ? 'No sessions found' : 'No sessions yet' }}
			</div>

			<div
				v-for="session in filteredSessions"
				:key="session.name"
				:class="[
					'session-item p-3 cursor-pointer hover:bg-gray-100 transition-colors border-b border-gray-100',
					isCurrentSession(session)
						? 'bg-blue-50 border-l-4 border-l-blue-500'
						: 'border-l-4 border-l-transparent'
				]"
				@click="$emit('select-session', session.name)"
			>
				<div class="flex items-start justify-between">
					<div class="flex-1 min-w-0">
						<div class="font-medium text-sm truncate text-gray-900">
							{{ session.agent_definition || 'Agent Session' }}
						</div>
						<div class="text-xs text-gray-500 mt-1 flex items-center space-x-2">
							<span>{{ formatTime(session.creation) }}</span>
						</div>
					</div>
					<Badge
						:label="formatStatus(session.status)"
						:theme="getStatusTheme(session.status)"
						size="sm"
					/>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, Badge } from 'frappe-ui'

const props = defineProps({
	sessions: {
		type: Array,
		default: () => []
	},
	currentSession: {
		type: Object,
		default: null
	}
})

defineEmits(['new-session', 'select-session'])

const searchQuery = ref('')

const filteredSessions = computed(() => {
	if (!searchQuery.value) {
		return props.sessions
	}

	const query = searchQuery.value.toLowerCase()
	return props.sessions.filter(session => {
		const agentDef = (session.agent_definition || '').toLowerCase()
		const name = (session.name || '').toLowerCase()
		return agentDef.includes(query) || name.includes(query)
	})
})

const isCurrentSession = (session) => {
	return props.currentSession && props.currentSession.name === session.name
}

const formatTime = (timestamp) => {
	if (!timestamp) return ''

	const date = new Date(timestamp)
	const now = new Date()
	const diffMs = now - date
	const diffMins = Math.floor(diffMs / 60000)
	const diffHours = Math.floor(diffMs / 3600000)
	const diffDays = Math.floor(diffMs / 86400000)

	if (diffMins < 1) return 'Just now'
	if (diffMins < 60) return `${diffMins}m ago`
	if (diffHours < 24) return `${diffHours}h ago`
	if (diffDays < 7) return `${diffDays}d ago`

	return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatStatus = (status) => {
	const statusMap = {
		'active': 'Active',
		'completed': 'Done',
		'error': 'Error',
		'timeout': 'Timeout'
	}
	return statusMap[status?.toLowerCase()] || status || 'Active'
}

const getStatusTheme = (status) => {
	const themes = {
		'active': 'green',
		'completed': 'blue',
		'error': 'red',
		'timeout': 'orange'
	}
	return themes[status?.toLowerCase()] || 'gray'
}
</script>

<style scoped>
.session-sidebar {
	width: 250px;
	min-width: 250px;
}
</style>
