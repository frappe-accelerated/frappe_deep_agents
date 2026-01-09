<template>
	<div class="activity-sidebar flex flex-col h-full bg-white border-l border-gray-200">
		<!-- Header -->
		<div class="p-4 border-b border-gray-200">
			<h3 class="font-semibold text-base text-gray-900">Agent Activity</h3>
			<AgentStatusIndicator :status="agentStatus" class="mt-2" />
		</div>

		<!-- Tabs -->
		<div class="border-b border-gray-200">
			<div class="flex space-x-1 px-4">
				<button
					v-for="tab in tabs"
					:key="tab.key"
					:class="[
						'py-2.5 px-3 border-b-2 font-medium text-sm transition-colors',
						activeTab === tab.key
							? 'border-blue-500 text-blue-600'
							: 'border-transparent text-gray-500 hover:text-gray-700'
					]"
					@click="activeTab = tab.key"
				>
					{{ tab.label }}
					<Badge
						v-if="tab.count > 0"
						:label="String(tab.count)"
						:theme="activeTab === tab.key ? 'blue' : 'gray'"
						size="sm"
						class="ml-1.5"
					/>
				</button>
			</div>
		</div>

		<!-- Content area -->
		<div class="flex-1 overflow-y-auto p-4">
			<!-- Tool Calls Tab -->
			<div v-if="activeTab === 'tools'">
				<div v-if="toolCalls.length === 0" class="text-center text-gray-500 text-sm py-8">
					<svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
					</svg>
					No tool calls yet
				</div>
				<div v-else class="space-y-3">
					<ToolCallCard
						v-for="(tool, index) in toolCalls"
						:key="tool.id || index"
						:tool-call="tool"
					/>
				</div>
			</div>

			<!-- Files Tab -->
			<div v-if="activeTab === 'files'">
				<div v-if="files.length === 0" class="text-center text-gray-500 text-sm py-8">
					<svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
					</svg>
					No files created yet
				</div>
				<AgentFileList v-else :files="files" @preview="handleFilePreview" />
			</div>

			<!-- Todos Tab -->
			<div v-if="activeTab === 'todos'">
				<div v-if="todos.length === 0" class="text-center text-gray-500 text-sm py-8">
					<svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
					</svg>
					No todos yet
				</div>
				<div v-else class="space-y-2">
					<div
						v-for="todo in todos"
						:key="todo.name"
						class="todo-item p-3 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors"
					>
						<div class="flex items-start space-x-3">
							<div
								:class="[
									'w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5',
									todo.status === 'completed'
										? 'bg-green-500'
										: todo.status === 'in_progress'
										? 'bg-blue-500'
										: 'border-2 border-gray-300'
								]"
							>
								<svg
									v-if="todo.status === 'completed'"
									class="w-3 h-3 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
								</svg>
								<div
									v-else-if="todo.status === 'in_progress'"
									class="w-2 h-2 bg-white rounded-full animate-pulse"
								></div>
							</div>
							<div class="flex-1 min-w-0">
								<div
									:class="[
										'text-sm',
										todo.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
									]"
								>
									{{ todo.description || todo.content }}
								</div>
								<div class="text-xs text-gray-500 mt-1">
									<Badge
										:label="formatTodoStatus(todo.status)"
										:theme="getTodoStatusTheme(todo.status)"
										size="sm"
									/>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Badge } from 'frappe-ui'
import AgentStatusIndicator from './AgentStatusIndicator.vue'
import ToolCallCard from './ToolCallCard.vue'
import AgentFileList from './AgentFileList.vue'

const props = defineProps({
	toolCalls: {
		type: Array,
		default: () => []
	},
	files: {
		type: Array,
		default: () => []
	},
	todos: {
		type: Array,
		default: () => []
	},
	agentStatus: {
		type: String,
		default: 'idle'
	}
})

const emit = defineEmits(['preview-file'])

const activeTab = ref('tools')

const tabs = computed(() => [
	{
		key: 'tools',
		label: 'Tools',
		count: props.toolCalls.length
	},
	{
		key: 'files',
		label: 'Files',
		count: props.files.length
	},
	{
		key: 'todos',
		label: 'Todos',
		count: props.todos.filter(t => t.status !== 'completed').length
	}
])

const handleFilePreview = (file) => {
	emit('preview-file', file)
}

const formatTodoStatus = (status) => {
	const statusMap = {
		'pending': 'Pending',
		'in_progress': 'In Progress',
		'completed': 'Completed'
	}
	return statusMap[status] || status
}

const getTodoStatusTheme = (status) => {
	const themes = {
		'pending': 'gray',
		'in_progress': 'blue',
		'completed': 'green'
	}
	return themes[status] || 'gray'
}
</script>

<style scoped>
.activity-sidebar {
	width: 380px;
	min-width: 380px;
}
</style>
