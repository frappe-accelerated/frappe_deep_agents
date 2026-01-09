import frappe

@frappe.whitelist()
def get_context():
	"""Return context for Agent Chat page"""
	return {
		"csrf_token": frappe.sessions.get_csrf_token(),
		"socketio_port": frappe.conf.get('socketio_port', 9000),
		"user": frappe.session.user,
		"user_image": frappe.db.get_value("User", frappe.session.user, "user_image")
	}
