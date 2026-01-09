<template>
	<div class="chat-interface flex flex-col h-full bg-white">
		<!-- Messages container -->
		<div ref="messagesContainer" class="messages-container flex-1 overflow-y-auto p-4 space-y-3">
			<div
				v-for="(msg, idx) in messages"
				:key="idx"
				:class="['message', msg.role, 'max-w-[85%] rounded-lg p-3 shadow-sm']"
			>
				<div class="message-role text-xs font-semibold text-gray-500 mb-1">
					{{ formatRole(msg.role) }}
				</div>
				<div class="message-content prose prose-sm max-w-none" v-html="renderContent(msg.content)"></div>
				<div v-if="msg.streaming" class="typing-indicator mt-2">
					<span></span><span></span><span></span>
				</div>
			</div>

			<div v-if="messages.length === 0" class="empty-state h-full flex items-center justify-center">
				<p class="text-gray-400">Start a conversation with the agent.</p>
			</div>
		</div>

		<!-- Input area -->
		<div class="input-area border-t p-4 bg-gray-50">
			<div class="flex gap-2">
				<textarea
					v-model="inputText"
					@keydown="handleKeydown"
					placeholder="Type your message... (Shift+Enter for new line, Enter to send)"
					:disabled="isStreaming"
					rows="3"
					class="flex-1 resize-none border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
				></textarea>
				<Button
					variant="solid"
					@click="send"
					:loading="isStreaming"
					:disabled="!inputText.trim() || isStreaming"
					class="self-end"
				>
					{{ isStreaming ? 'Processing...' : 'Send' }}
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Button } from 'frappe-ui'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import 'highlight.js/styles/github.css'

// Register highlight.js languages
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('bash', bash)

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

const inputText = ref('')
const messagesContainer = ref(null)

// Configure marked for better markdown rendering
marked.setOptions({
	breaks: true,
	gfm: true,
	highlight: function(code, lang) {
		if (lang && hljs.getLanguage(lang)) {
			try {
				return hljs.highlight(code, { language: lang }).value
			} catch (err) {
				console.error('Highlight error:', err)
			}
		}
		return code
	}
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

function handleKeydown(e) {
	if (e.key === 'Enter' && !e.shiftKey) {
		e.preventDefault()
		send()
	}
}

function send() {
	if (inputText.value.trim() && !props.isStreaming) {
		emit('send', inputText.value)
		inputText.value = ''
	}
}

function formatRole(role) {
	const roles = {
		user: 'You',
		assistant: 'Agent',
		system: 'System',
		tool: 'Tool'
	}
	return roles[role] || role
}

function renderContent(content) {
	if (!content) return ''

	try {
		return marked.parse(content)
	} catch (err) {
		console.error('Markdown parse error:', err)
		return content.replace(/\n/g, '<br>')
	}
}
</script>
