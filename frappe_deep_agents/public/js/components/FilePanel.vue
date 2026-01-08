<template>
  <div class="file-panel">
    <div class="panel-header">
      <h4>Files</h4>
      <button class="btn btn-xs btn-default" @click="$emit('refresh')">
        ↻
      </button>
    </div>

    <div class="file-list">
      <div
        v-for="file in files"
        :key="file.name"
        :class="['file-item', { directory: file.is_directory }]"
        @click="$emit('open', file)"
      >
        <span class="file-icon">
          {{ file.is_directory ? '📁' : '📄' }}
        </span>
        <span class="file-name">{{ file.file_path }}</span>
      </div>

      <div v-if="files.length === 0" class="empty-state">
        No files yet
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  files: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['open', 'refresh'])
</script>

<style scoped>
.file-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
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

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.file-item:hover {
  background: var(--gray-50);
}

.file-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.file-name {
  font-size: 0.875rem;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}
</style>
