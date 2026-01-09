import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import AgentWorkspace from './pages/AgentWorkspace.vue'

const routes = [
	{
		path: '/agent',
		name: 'Home',
		component: Home
	},
	{
		path: '/agent/workspace/:sessionId?',
		name: 'Workspace',
		component: AgentWorkspace,
		props: true
	}
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

export default router
