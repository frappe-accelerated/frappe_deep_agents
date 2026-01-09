import { io } from 'socket.io-client'

class SocketService {
	constructor() {
		this.socket = null
		this.connected = false
	}

	connect() {
		if (this.socket) return this.socket

		// Use Frappe's Socket.IO server
		const port = window.frappe?.socketio_port || 9000
		const host = window.location.hostname

		this.socket = io(`${window.location.protocol}//${host}:${port}`, {
			withCredentials: true,
			reconnection: true,
			reconnectionDelay: 1000,
			reconnectionAttempts: 5
		})

		this.socket.on('connect', () => {
			this.connected = true
			console.log('Socket.IO connected')
		})

		this.socket.on('disconnect', () => {
			this.connected = false
			console.log('Socket.IO disconnected')
		})

		this.socket.on('connect_error', (error) => {
			console.error('Socket.IO connection error:', error)
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
	}

	on(event, callback) {
		if (!this.socket) this.connect()
		this.socket.on(event, callback)
	}

	off(event, callback) {
		if (!this.socket) return
		this.socket.off(event, callback)
	}

	disconnect() {
		if (this.socket) {
			this.socket.disconnect()
			this.socket = null
			this.connected = false
		}
	}
}

export default new SocketService()
