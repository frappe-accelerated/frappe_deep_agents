// Date formatting helper
export function formatDate(dateString) {
	const date = new Date(dateString)
	const now = new Date()
	const diff = now - date
	const seconds = Math.floor(diff / 1000)
	const minutes = Math.floor(seconds / 60)
	const hours = Math.floor(minutes / 60)
	const days = Math.floor(hours / 24)

	if (seconds < 60) return 'just now'
	if (minutes < 60) return `${minutes}m ago`
	if (hours < 24) return `${hours}h ago`
	if (days < 7) return `${days}d ago`

	return date.toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
	})
}

// Get status theme color
export function getStatusTheme(status) {
	const themes = {
		'Active': 'green',
		'Ended': 'gray',
		'Error': 'red',
		'Processing': 'blue'
	}
	return themes[status] || 'gray'
}

// Format role name for display
export function formatRole(role) {
	const roles = {
		'user': 'You',
		'assistant': 'Agent',
		'system': 'System',
		'tool': 'Tool'
	}
	return roles[role] || role
}

// Truncate text with ellipsis
export function truncate(text, length = 100) {
	if (!text || text.length <= length) return text
	return text.substring(0, length) + '...'
}

// Get file icon based on extension
export function getFileIcon(filename) {
	const ext = filename.split('.').pop().toLowerCase()
	const icons = {
		'js': '📜',
		'py': '🐍',
		'vue': '💚',
		'html': '🌐',
		'css': '🎨',
		'json': '📋',
		'md': '📝',
		'txt': '📄',
		'png': '🖼️',
		'jpg': '🖼️',
		'jpeg': '🖼️',
		'gif': '🖼️',
		'svg': '🖼️',
		'pdf': '📕',
		'zip': '📦',
		'tar': '📦',
		'gz': '📦'
	}
	return icons[ext] || '📁'
}

// Copy text to clipboard
export async function copyToClipboard(text) {
	try {
		await navigator.clipboard.writeText(text)
		return true
	} catch (err) {
		console.error('Failed to copy:', err)
		return false
	}
}
