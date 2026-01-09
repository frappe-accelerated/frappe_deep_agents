# Frappe Deep Agents - Frontend

This is the standalone SPA frontend for Frappe Deep Agents, built with Vue 3, Frappe UI, and Vite.

## Features

- 🤖 Real-time agent chat interface with Socket.IO streaming
- ✅ Todo tracking panel
- 📁 File browser panel
- 🎨 Frappe UI components for consistent design
- 📝 Markdown rendering with syntax highlighting
- 🚀 Fast development with Vite HMR

## Development

### Prerequisites

- Node.js 16+ and npm
- Running Frappe bench instance

### Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Access the app at: http://localhost:8081/agent

The dev server proxies API requests to localhost:8000 and Socket.IO to localhost:9000.

### Development Workflow

- Edit files in `src/`
- Changes auto-reload in browser
- Vue DevTools available for debugging

## Production Build

### Build Assets

```bash
cd frontend
npm run build
```

This creates production-optimized assets in:
```
frappe_deep_agents/public/frontend/
├── assets/
│   ├── frappe-ui-*.css
│   ├── frappe-ui-*.js
│   ├── index-*.css
│   ├── index-*.js
│   ├── markdown-*.js
│   └── socket-*.js
└── index.html
```

### Deploy to Frappe

After building, the assets are automatically available at:
- URL: `/agent`
- Route: Handled by `frappe_deep_agents/www/agent.py` and `agent.html`

### Restart Frappe

```bash
bench restart
```

Access the app at: `http://your-site:8000/agent`

## Project Structure

```
frontend/
├── src/
│   ├── main.js              # App entry point
│   ├── App.vue              # Root component
│   ├── router.js            # Vue Router config
│   ├── socket.js            # Socket.IO client
│   ├── index.css            # Global styles
│   ├── pages/
│   │   ├── Home.vue         # Sessions list
│   │   └── AgentWorkspace.vue  # Main workspace
│   ├── components/
│   │   ├── ChatInterface.vue   # Chat UI
│   │   ├── TodoPanel.vue       # Todos sidebar
│   │   └── FilePanel.vue       # Files sidebar
│   └── utils/
│       ├── api.js           # API helpers
│       └── helpers.js       # Utility functions
├── index.html               # HTML template
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies
└── tailwind.config.js      # Tailwind CSS config
```

## Key Technologies

- **Vue 3**: Composition API, reactive data
- **Vue Router**: Client-side routing
- **Frappe UI**: Official Frappe component library
- **Socket.IO Client**: Real-time streaming
- **Marked**: Markdown parsing
- **Highlight.js**: Code syntax highlighting
- **Tailwind CSS**: Utility-first CSS
- **Vite**: Fast build tool and dev server

## API Integration

The frontend communicates with the backend via:

1. **REST API** (`/api/method/frappe_deep_agents.api.*`):
   - `create_session()` - Create agent session
   - `get_session()` - Get session details
   - `send_message()` - Send user message
   - `end_session()` - End active session
   - `list_agents()` - Get available agents
   - `list_sessions()` - Get session history
   - `update_todo()` - Update todo status

2. **Socket.IO** (port 9000):
   - `agent_token` - Token streaming
   - `todo_update` - Todo changes
   - `file_update` - File changes
   - `agent_complete` - Execution complete
   - `agent_error` - Error messages

## Troubleshooting

### Build fails
- Clear node_modules and package-lock.json
- Run `npm install` again
- Check Node.js version (16+)

### Dev server won't start
- Check port 8081 is available
- Verify Frappe bench is running on port 8000
- Check Socket.IO is on port 9000

### Components not rendering
- Check browser console for errors
- Verify frappe-ui is installed correctly
- Check Vite config for plugin issues

### API calls failing
- Verify CSRF token is passed
- Check network tab for 403/401 errors
- Ensure user is logged in to Frappe

## License

MIT
