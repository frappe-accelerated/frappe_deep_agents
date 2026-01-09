import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import AgentWorkspace from './pages/AgentWorkspace.vue'

const routes = [
	{
		path: '/app/agent-chat',
		name: 'Home',
		component: AgentWorkspace
	},
	{
		path: '/app/agent-chat/:sessionId',
		name: 'WorkspaceWithSession',
		component: AgentWorkspace,
		props: true
	},
	{
		path: '/agent',
		name: 'AgentHome',
		component: AgentWorkspace
	},
	{
		path: '/agent/workspace',
		name: 'Workspace',
		component: AgentWorkspace
	},
	{
		path: '/agent/workspace/:sessionId',
		name: 'WorkspaceSession',
		component: AgentWorkspace,
		props: true
	},
	// Fallback redirect
	{
		path: '/:pathMatch(.*)*',
		redirect: '/app/agent-chat'
	}
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

export default router
