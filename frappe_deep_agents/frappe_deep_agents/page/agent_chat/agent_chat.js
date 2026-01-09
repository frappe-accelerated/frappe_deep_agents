frappe.pages['agent-chat'].on_page_load = function(wrapper) {
	// Create the page with full-height container
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Deep Agents',
		single_column: true
	});

	// Hide the standard Frappe page elements for a cleaner look
	page.main.css({
		'padding': '0',
		'height': 'calc(100vh - 60px)'  // Account for navbar
	});

	// Hide page header for full immersion
	$(wrapper).find('.page-head').hide();

	// Add Vue app mount point
	$(page.main).html(`
		<div id="agent-chat-app" style="width: 100%; height: 100%;"></div>
	`);

	// Set up context and initialize Vue app
	frappe.call({
		method: 'frappe_deep_agents.frappe_deep_agents.page.agent_chat.agent_chat.get_context',
		callback: function(r) {
			if (r.message) {
				window.frappe = window.frappe || {};
				window.frappe.csrf_token = r.message.csrf_token;
				window.frappe.socketio_port = r.message.socketio_port;
				window.frappe.user = r.message.user;
				window.frappe.user_image = r.message.user_image;
			}
		}
	});
};
