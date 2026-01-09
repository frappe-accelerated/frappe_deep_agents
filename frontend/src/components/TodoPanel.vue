<template>
	<div class="todo-panel flex flex-col border-b max-h-1/2">
		<!-- Header -->
		<div class="panel-header flex justify-between items-center px-4 py-3 bg-gray-50 border-b">
			<h4 class="m-0 text-sm font-semibold">Todos</h4>
			<span class="text-xs text-gray-500">{{ completedCount }}/{{ todos.length }}</span>
		</div>

		<!-- Todo list -->
		<div class="todo-list flex-1 overflow-y-auto p-2">
			<div
				v-for="todo in todos"
				:key="todo.name"
				:class="[
					'todo-item flex items-center gap-2 p-2 rounded transition-colors',
					{
						'bg-yellow-50': todo.status === 'in_progress',
						'hover:bg-gray-50': todo.status !== 'in_progress'
					}
				]"
			>
				<button
					:class="[
						'todo-checkbox w-5 h-5 flex items-center justify-center rounded border-2 flex-shrink-0 text-xs',
						{
							'bg-green-500 border-green-500 text-white': todo.status === 'completed',
							'bg-yellow-100 border-yellow-400': todo.status === 'in_progress',
							'bg-white border-gray-300 cursor-pointer': todo.status === 'pending'
						}
					]"
					@click="toggleTodo(todo)"
					:disabled="todo.status === 'in_progress'"
				>
					<span v-if="todo.status === 'completed'">✓</span>
					<span v-else-if="todo.status === 'in_progress'">⏳</span>
				</button>
				<span
					:class="[
						'todo-text text-sm leading-snug',
						{ 'line-through text-gray-500': todo.status === 'completed' }
					]"
				>
					{{ todo.description }}
				</span>
			</div>

			<div v-if="todos.length === 0" class="empty-state text-center p-4 text-gray-500 text-sm">
				No todos yet
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	todos: {
		type: Array,
		default: () => []
	}
})

const emit = defineEmits(['update'])

const completedCount = computed(() => {
	return props.todos.filter(t => t.status === 'completed').length
})

function toggleTodo(todo) {
	if (todo.status === 'in_progress') return

	const newStatus = todo.status === 'completed' ? 'pending' : 'completed'
	emit('update', todo.name, newStatus)
}
</script>
