<template>
  <div class="agent-status flex items-center space-x-2 text-sm">
    <div
      :class="[
        'w-2 h-2 rounded-full',
        statusColor,
        { 'animate-pulse': isActive }
      ]"
    ></div>
    <span class="text-gray-600">{{ statusText }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'idle'
  }
})

const isActive = computed(() =>
  ['running', 'streaming', 'thinking'].includes(props.status)
)

const statusColor = computed(() => {
  const colors = {
    'idle': 'bg-gray-400',
    'running': 'bg-blue-500',
    'streaming': 'bg-green-500',
    'thinking': 'bg-purple-500',
    'error': 'bg-red-500',
    'completed': 'bg-green-500'
  }
  return colors[props.status] || 'bg-gray-400'
})

const statusText = computed(() => {
  const texts = {
    'idle': 'Waiting for input',
    'running': 'Processing...',
    'streaming': 'Generating response...',
    'thinking': 'Thinking...',
    'error': 'Error occurred',
    'completed': 'Ready'
  }
  return texts[props.status] || 'Unknown status'
})
</script>
