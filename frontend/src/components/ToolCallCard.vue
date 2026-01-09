<template>
	<div
		:class="[
			'tool-call-card border rounded-lg p-3 cursor-pointer transition-all',
			statusClass
		]"
		@click="toggleExpanded"
	>
		<!-- Summary View -->
		<div class="flex items-start justify-between">
			<div class="flex items-start space-x-2 flex-1">
				<!-- Status Icon -->
				<div :class="['w-5 h-5 mt-0.5 flex-shrink-0', statusColor]">
					<!-- Running -->
					<svg v-if="toolCall.status === 'running'" class="animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
					</svg>
					<!-- Success -->
					<svg v-else-if="toolCall.status === 'success'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<!-- Error -->
					<svg v-else-if="toolCall.status === 'error'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<!-- Pending -->
					<svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<div class="flex-1 min-w-0">
					<div class="font-medium text-sm truncate">{{ toolCall.tool_name }}</div>
					<div class="text-xs text-gray-500 mt-0.5">{{ formatTime(toolCall.timestamp) }}</div>
				</div>
			</div>
			<svg
				:class="[
					'w-4 h-4 text-gray-400 transform transition-transform flex-shrink-0 ml-2',
					{ 'rotate-180': isExpanded }
				]"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</div>

		<!-- Expanded Details -->
		<div v-if="isExpanded" class="mt-3 pt-3 border-t space-y-2">
			<!-- Input -->
			<div v-if="toolCall.input">
				<div class="text-xs font-medium text-gray-600 mb-1">Input</div>
				<pre class="text-xs bg-gray-50 p-2 rounded overflow-x-auto border border-gray-200 max-h-40">{{ formatJson(toolCall.input) }}</pre>
			</div>

			<!-- Output -->
			<div v-if="toolCall.output">
				<div class="text-xs font-medium text-gray-600 mb-1">Output</div>
				<pre class="text-xs bg-gray-50 p-2 rounded overflow-x-auto border border-gray-200 max-h-40">{{ truncateOutput(toolCall.output) }}</pre>
			</div>

			<!-- Error -->
			<div v-if="toolCall.error" class="bg-red-50 p-2 rounded border border-red-200">
				<div class="text-xs font-medium text-red-600 mb-1">Error</div>
				<pre class="text-xs text-red-700 whitespace-pre-wrap">{{ toolCall.error }}</pre>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
	toolCall: {
		type: Object,
		required: true
	}
})

const isExpanded = ref(false)

const toggleExpanded = () => {
	isExpanded.value = !isExpanded.value
}

const statusClass = {
	'border-blue-200 bg-blue-50': props.toolCall.status === 'running',
	'border-green-200 bg-green-50': props.toolCall.status === 'success',
	'border-red-200 bg-red-50': props.toolCall.status === 'error',
	'border-gray-200 bg-white': props.toolCall.status === 'pending'
}

const statusColor = {
	'text-blue-500': props.toolCall.status === 'running',
	'text-green-500': props.toolCall.status === 'success',
	'text-red-500': props.toolCall.status === 'error',
	'text-gray-400': props.toolCall.status === 'pending'
}

const formatTime = (timestamp) => {
	if (!timestamp) return ''

	const date = new Date(timestamp)
	return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

const formatJson = (value) => {
	if (typeof value === 'string') {
		try {
			return JSON.stringify(JSON.parse(value), null, 2)
		} catch {
			return value
		}
	} else if (typeof value === 'object') {
		return JSON.stringify(value, null, 2)
	}
	return String(value)
}

const truncateOutput = (value) => {
	const formatted = formatJson(value)
	if (formatted.length > 500) {
		return formatted.substring(0, 500) + '\n... (truncated)'
	}
	return formatted
}
</script>
