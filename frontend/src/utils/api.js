/**
 * API utility functions for Frappe Deep Agents
 */

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
		const error = await response.json().catch(() => ({}))
		throw new Error(error.exception || error.message || `API call failed: ${response.status}`)
	}

	const data = await response.json()
	return data.message
}

// Specific API methods for Deep Agents
export const agentAPI = {
	/**
	 * Create a new agent session
	 * @param {string} agentDefinition - Name of the Agent Definition
	 * @returns {Promise<Object>} - Created session object
	 */
	createSession: (agentDefinition) =>
		call('frappe_deep_agents.api.create_session', { agent_definition: agentDefinition }),

	/**
	 * Get session details including messages, todos, and files
	 * @param {string} sessionId - Name of the Agent Session
	 * @returns {Promise<Object>} - Session details
	 */
	getSession: (sessionId) =>
		call('frappe_deep_agents.api.get_session', { session_id: sessionId }),

	/**
	 * Send a message to the agent
	 * @param {string} sessionId - Name of the Agent Session
	 * @param {string} message - User message content
	 * @returns {Promise<Object>} - Status response
	 */
	sendMessage: (sessionId, message) =>
		call('frappe_deep_agents.api.send_message', { session_id: sessionId, message }),

	/**
	 * End an agent session
	 * @param {string} sessionId - Name of the Agent Session
	 * @returns {Promise<Object>} - Status response
	 */
	endSession: (sessionId) =>
		call('frappe_deep_agents.api.end_session', { session_id: sessionId }),

	/**
	 * List all available agent definitions
	 * @returns {Promise<Array>} - List of agent definitions
	 */
	listAgents: () =>
		call('frappe_deep_agents.api.list_agents'),

	/**
	 * List agent sessions with optional filters
	 * @param {string|null} agentDefinition - Filter by agent definition
	 * @param {string|null} status - Filter by status
	 * @returns {Promise<Array>} - List of sessions
	 */
	listSessions: (agentDefinition = null, status = null) =>
		call('frappe_deep_agents.api.list_sessions', { agent_definition: agentDefinition, status }),

	/**
	 * Update a todo item's status
	 * @param {string} todoName - Name of the Agent Todo
	 * @param {string} status - New status (pending/in_progress/completed)
	 * @returns {Promise<Object>} - Updated todo
	 */
	updateTodo: (todoName, status) =>
		call('frappe_deep_agents.api.update_todo', { todo_name: todoName, status }),

	/**
	 * Get file content from an agent file
	 * @param {string} fileName - Name of the Agent File document
	 * @returns {Promise<string>} - File content
	 */
	getFileContent: (fileName) =>
		call('frappe_deep_agents.api.get_file_content', { file_name: fileName }),

	/**
	 * Export agent configuration to YAML
	 * @param {string} agentDefinition - Name of the Agent Definition
	 * @returns {Promise<string>} - YAML content
	 */
	exportAgentYaml: (agentDefinition) =>
		call('frappe_deep_agents.api.export_agent_yaml', { agent_definition: agentDefinition }),

	/**
	 * Import agent configuration from YAML
	 * @param {string} yamlContent - YAML configuration content
	 * @returns {Promise<Object>} - Import result
	 */
	importAgentYaml: (yamlContent) =>
		call('frappe_deep_agents.api.import_agent_yaml', { yaml_content: yamlContent })
}
