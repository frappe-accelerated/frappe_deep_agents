import frappe

def get_context(context):
	"""
	Context for agent SPA route.

	Frappe will serve agent.html for all /agent/* routes.
	The Vue Router handles client-side routing.
	"""
	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access Deep Agents", frappe.PermissionError)

	# Get CSRF token for API calls
	context.csrf_token = frappe.sessions.get_csrf_token()

	# Get Socket.IO configuration
	context.socketio_port = frappe.conf.get('socketio_port', 9000)

	# Get user info
	context.user = frappe.session.user
	context.user_image = frappe.db.get_value("User", frappe.session.user, "user_image")

	# Add app version for cache busting
	context.build_version = frappe.utils.get_build_version()

	return context
