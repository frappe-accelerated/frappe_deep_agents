<template>
  <div class="todo-panel">
    <div class="panel-header">
      <h4>Todos</h4>
      <span class="todo-count">{{ completedCount }}/{{ todos.length }}</span>
    </div>

    <div class="todo-list">
      <div
        v-for="todo in todos"
        :key="todo.name"
        :class="['todo-item', todo.status]"
      >
        <button
          class="todo-checkbox"
          @click="toggleTodo(todo)"
          :disabled="todo.status === 'in_progress'"
        >
          <span v-if="todo.status === 'completed'">✓</span>
          <span v-else-if="todo.status === 'in_progress'">⏳</span>
        </button>
        <span class="todo-text">{{ todo.description }}</span>
      </div>

      <div v-if="todos.length === 0" class="empty-state">
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
  const newStatus = todo.status === 'completed' ? 'pending' : 'completed'
  emit('update', todo.name, newStatus)
}
</script>

<style scoped>
.todo-panel {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--border-color);
  max-height: 50%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-color);
}

.panel-header h4 {
  margin: 0;
  font-size: 0.875rem;
}

.todo-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.todo-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.15s;
}

.todo-item:hover {
  background: var(--gray-50);
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: var(--text-muted);
}

.todo-item.in_progress {
  background: var(--yellow-50);
}

.todo-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.todo-item.completed .todo-checkbox {
  background: var(--green-500);
  border-color: var(--green-500);
  color: white;
}

.todo-item.in_progress .todo-checkbox {
  background: var(--yellow-100);
  border-color: var(--yellow-400);
}

.todo-checkbox:disabled {
  cursor: not-allowed;
}

.todo-text {
  font-size: 0.875rem;
  line-height: 1.4;
}

.empty-state {
  text-align: center;
  padding: 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}
</style>
