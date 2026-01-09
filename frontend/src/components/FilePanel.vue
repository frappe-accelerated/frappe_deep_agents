<template>
	<div class="file-panel flex flex-col flex-1 overflow-hidden">
		<!-- Header -->
		<div class="panel-header flex justify-between items-center px-4 py-3 bg-gray-50 border-b">
			<h4 class="m-0 text-sm font-semibold">Files</h4>
			<Button size="sm" @click="$emit('refresh')" icon="refresh-ccw">
				Refresh
			</Button>
		</div>

		<!-- File list -->
		<div class="file-list flex-1 overflow-y-auto p-2">
			<div
				v-for="file in files"
				:key="file.name"
				:class="[
					'file-item flex items-center gap-2 p-2 rounded cursor-pointer transition-colors',
					'hover:bg-gray-50'
				]"
				@click="$emit('open', file)"
			>
				<span class="file-icon text-base flex-shrink-0">
					{{ getFileIcon(file) }}
				</span>
				<span class="file-name text-sm font-mono overflow-hidden text-ellipsis whitespace-nowrap">
					{{ file.file_path }}
				</span>
			</div>

			<div v-if="files.length === 0" class="empty-state text-center p-4 text-gray-500 text-sm">
				No files yet
			</div>
		</div>
	</div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import { getFileIcon as getIcon } from '../utils/helpers'

const props = defineProps({
	files: {
		type: Array,
		default: () => []
	}
})

const emit = defineEmits(['open', 'refresh'])

function getFileIcon(file) {
	if (file.is_directory) return '📁'
	return getIcon(file.file_path)
}
</script>
