export async function call(method, args = {}) {
	const response = await fetch('/api/method/' + method, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-Frappe-CSRF-Token': window.frappe?.csrf_token || ''
		},
		body: JSON.stringify(args)
	})

	if (!response.ok) {
		const error = await response.json()
		throw new Error(error.exception || error.message || 'API call failed')
	}

	const data = await response.json()
	return data.message
}

// Specific API methods for Deep Agents
export const agentAPI = {
	createSession: (agentDefinition) =>
		call('frappe_deep_agents.api.create_session', { agent_definition: agentDefinition }),

	getSession: (sessionId) =>
		call('frappe_deep_agents.api.get_session', { session_id: sessionId }),

	sendMessage: (sessionId, message) =>
		call('frappe_deep_agents.api.send_message', { session_id: sessionId, message }),

	endSession: (sessionId) =>
		call('frappe_deep_agents.api.end_session', { session_id: sessionId }),

	listAgents: () =>
		call('frappe_deep_agents.api.list_agents'),

	listSessions: (agentDefinition = null, status = null) =>
		call('frappe_deep_agents.api.list_sessions', { agent_definition: agentDefinition, status }),

	updateTodo: (todoName, status) =>
		call('frappe_deep_agents.api.update_todo', { todo_name: todoName, status }),

	getFileContent: (fileName) =>
		call('frappe_deep_agents.api.get_file_content', { file_name: fileName })
}
