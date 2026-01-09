<template>
  <div class="chat-input border-t bg-white p-4">
    <div class="max-w-3xl mx-auto">
      <div class="flex items-end space-x-3">
        <textarea
          ref="textareaRef"
          v-model="inputText"
          :disabled="disabled"
          placeholder="Send a message... (Shift+Enter for new line)"
          rows="1"
          class="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          @keydown="handleKeydown"
          @input="adjustHeight"
        ></textarea>

        <button
          :disabled="disabled || !inputText.trim()"
          @click="send"
          :class="[
            'px-6 py-3 rounded-xl font-medium transition-colors flex items-center justify-center',
            disabled || !inputText.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          ]"
        >
          <svg v-if="!disabled" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      <div v-if="inputText.length > 0" class="text-xs text-gray-500 mt-2 text-right">
        {{ inputText.length }} characters
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

const inputText = ref('')
const textareaRef = ref(null)

const send = () => {
  if (inputText.value.trim() && !props.disabled) {
    emit('send', inputText.value.trim())
    inputText.value = ''
    nextTick(() => adjustHeight())
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

const adjustHeight = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
  }
}
</script>
