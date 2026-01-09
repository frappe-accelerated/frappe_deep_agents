<template>
	<div class="agent-file-list">
		<div v-if="!files.length" class="text-center text-gray-500 text-sm py-8">
			<svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
			</svg>
			No files created yet
		</div>

		<div v-else class="space-y-2">
			<div
				v-for="file in files"
				:key="file.name"
				class="file-item flex items-center p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors border border-gray-200"
				@click="$emit('preview', file)"
			>
				<div class="text-xl mr-3">{{ getFileIcon(file.file_path || file.name) }}</div>
				<div class="flex-1 min-w-0">
					<div class="font-medium text-sm truncate text-gray-900">{{ getFileName(file.file_path || file.name) }}</div>
					<div class="text-xs text-gray-500 truncate">
						{{ file.file_path || file.name }}
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
defineProps({
	files: {
		type: Array,
		default: () => []
	}
})

defineEmits(['preview'])

const getFileName = (path) => {
	if (!path) return 'Unknown'
	const parts = path.split('/')
	return parts[parts.length - 1]
}

const getFileIcon = (typeOrName) => {
	// Try to determine type from name if type not provided
	const name = typeOrName || ''
	const ext = name.includes('.') ? name.split('.').pop().toLowerCase() : ''

	const icons = {
		'py': '🐍',
		'python': '🐍',
		'js': '📜',
		'javascript': '📜',
		'ts': '📘',
		'typescript': '📘',
		'vue': '💚',
		'json': '📋',
		'md': '📝',
		'markdown': '📝',
		'txt': '📄',
		'text': '📄',
		'png': '🖼️',
		'jpg': '🖼️',
		'jpeg': '🖼️',
		'gif': '🖼️',
		'svg': '🎨',
		'pdf': '📕',
		'html': '🌐',
		'css': '🎨',
		'yaml': '⚙️',
		'yml': '⚙️',
		'xml': '📰',
		'csv': '📊',
		'sql': '🗄️',
		'sh': '💻',
		'bash': '💻',
		'dockerfile': '🐳',
		'docker': '🐳'
	}
	return icons[ext] || '📄'
}
</script>
