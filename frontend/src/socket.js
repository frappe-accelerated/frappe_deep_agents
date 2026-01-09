import { io } from 'socket.io-client'

class SocketService {
	constructor() {
		this.socket = null
		this.connected = false
		this.eventHandlers = new Map()
	}

	connect() {
		if (this.socket && this.connected) return this.socket

		// Use Frappe's Socket.IO server
		const port = window.frappe?.socketio_port || 9000
		const host = window.location.hostname

		this.socket = io(`${window.location.protocol}//${host}:${port}`, {
			withCredentials: true,
			reconnection: true,
			reconnectionDelay: 1000,
			reconnectionAttempts: 10,
			timeout: 20000
		})

		this.socket.on('connect', () => {
			this.connected = true
			console.log('Socket.IO connected')
		})

		this.socket.on('disconnect', (reason) => {
			this.connected = false
			console.log('Socket.IO disconnected:', reason)
		})

		this.socket.on('connect_error', (error) => {
			console.error('Socket.IO connection error:', error)
		})

		this.socket.on('reconnect', (attemptNumber) => {
			console.log('Socket.IO reconnected after', attemptNumber, 'attempts')
		})

		return this.socket
	}

	subscribe(channel) {
		if (!this.socket) this.connect()
		this.socket.emit('subscribe', channel)
		console.log('Subscribed to channel:', channel)
	}

	unsubscribe(channel) {
		if (!this.socket) return
		this.socket.emit('unsubscribe', channel)
		console.log('Unsubscribed from channel:', channel)

		// Clean up event handlers for this channel
		this.eventHandlers.delete(channel)
	}

	on(event, callback) {
		if (!this.socket) this.connect()
		this.socket.on(event, callback)
	}

	off(event, callback) {
		if (!this.socket) return
		if (callback) {
			this.socket.off(event, callback)
		} else {
			this.socket.off(event)
		}
	}

	// Remove all listeners for a specific event
	removeAllListeners(event) {
		if (!this.socket) return
		this.socket.removeAllListeners(event)
	}

	emit(event, data) {
		if (!this.socket) this.connect()
		this.socket.emit(event, data)
	}

	disconnect() {
		if (this.socket) {
			this.socket.disconnect()
			this.socket = null
			this.connected = false
			this.eventHandlers.clear()
		}
	}

	isConnected() {
		return this.connected && this.socket?.connected
	}
}

// Singleton instance
const socketService = new SocketService()

export default socketService

// Event types for reference
export const SOCKET_EVENTS = {
	AGENT_TOKEN: 'agent_token',
	TOOL_CALL_START: 'tool_call_start',
	TOOL_CALL_COMPLETE: 'tool_call_complete',
	AGENT_STATUS: 'agent_status',
	TODO_UPDATE: 'todo_update',
	FILE_UPDATE: 'file_update',
	AGENT_COMPLETE: 'agent_complete',
	AGENT_ERROR: 'agent_error'
}
