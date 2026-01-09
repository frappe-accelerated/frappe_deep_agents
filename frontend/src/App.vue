<template>
	<div id="app" class="h-screen w-screen bg-gray-50">
		<router-view />
	</div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import socketService from './socket'

onMounted(() => {
	// Initialize socket connection
	socketService.connect()

	// Fetch CSRF token if not already available
	if (!window.frappe?.csrf_token) {
		fetch('/api/method/frappe.auth.get_logged_user')
			.then(res => res.json())
			.catch(console.error)
	}
})

onUnmounted(() => {
	socketService.disconnect()
})
</script>
