<template>
	<div class="chat-interface flex flex-col h-full bg-white">
		<!-- Messages container -->
		<div ref="messagesContainer" class="messages-container flex-1 overflow-y-auto px-4 py-6">
			<div class="max-w-3xl mx-auto space-y-4">
				<!-- Empty state -->
				<div v-if="messages.length === 0 && !isStreaming" class="h-full flex items-center justify-center min-h-96">
					<div class="text-center">
						<div class="text-5xl mb-4">🤖</div>
						<h2 class="text-xl font-semibold text-gray-900 mb-2">Start a conversation</h2>
						<p class="text-gray-500">
							Send a message to begin interacting with the agent.
						</p>
					</div>
				</div>

				<!-- Messages -->
				<ChatMessage
					v-for="(msg, idx) in messages"
					:key="idx"
					:message="msg"
				/>

				<!-- Typing indicator -->
				<div v-if="isStreaming && !lastMessageHasContent" class="flex items-center space-x-2 text-gray-500">
					<div class="typing-indicator flex space-x-1">
						<span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms;"></span>
						<span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms;"></span>
						<span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms;"></span>
					</div>
					<span class="text-sm">Agent is thinking...</span>
				</div>
			</div>
		</div>

		<!-- Input area -->
		<ChatInput
			:disabled="isStreaming"
			@send="handleSend"
		/>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'

const props = defineProps({
	messages: {
		type: Array,
		default: () => []
	},
	isStreaming: {
		type: Boolean,
		default: false
	}
})

const emit = defineEmits(['send'])

const messagesContainer = ref(null)

// Check if the last message has content (for showing typing indicator)
const lastMessageHasContent = computed(() => {
	if (props.messages.length === 0) return false
	const lastMsg = props.messages[props.messages.length - 1]
	return lastMsg && lastMsg.content && lastMsg.content.length > 0
})

// Auto-scroll on new messages
watch(
	() => props.messages.length,
	() => {
		nextTick(() => {
			scrollToBottom()
		})
	}
)

// Also scroll when streaming content updates
watch(
	() => props.messages[props.messages.length - 1]?.content,
	() => {
		nextTick(() => {
			scrollToBottom()
		})
	},
	{ deep: true }
)

function scrollToBottom() {
	if (messagesContainer.value) {
		messagesContainer.value.scrollTo({
			top: messagesContainer.value.scrollHeight,
			behavior: 'smooth'
		})
	}
}

function handleSend(message) {
	emit('send', message)
}
</script>

<style scoped>
@keyframes bounce {
	0%, 100% {
		transform: translateY(0);
	}
	50% {
		transform: translateY(-4px);
	}
}

.animate-bounce {
	animation: bounce 0.6s infinite;
}
</style>
