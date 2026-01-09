app_name = "frappe_deep_agents"
app_title = "Frappe Deep Agents"
app_publisher = "Frappe Accelerated"
app_description = "LangChain Deep Agents implementation for Frappe with Kubernetes sandbox support"
app_email = "admin@frappe-accelerated.com"
app_license = "MIT"
app_icon = "octicon octicon-hubot"
app_color = "purple"

# Required apps
required_apps = ["frappe"]

# Website route rules
website_route_rules = [
	{"from_route": "/agent/<path:app_path>", "to_route": "agent"},
]

# Include frontend assets (built by Vite)
# These will be available after running: cd frontend && npm run build
app_include_js = []
app_include_css = []

# Scheduled Tasks
scheduler_events = {
	"hourly": [
		"frappe_deep_agents.tasks.cleanup_sessions"
	],
}

# Fixtures
fixtures = [
	{"doctype": "Custom Field", "filters": [["module", "=", "Frappe Deep Agents"]]},
	{"doctype": "Workspace", "filters": [["module", "=", "Frappe Deep Agents"]]},
]
