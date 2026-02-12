# PLC Control Panel - Vue.js Edition

A modern web-based PLC control panel built with Vue.js and Node.js, replicating the functionality of the Python/Tkinter version.

## 🏗️ Project Structure

```
PLC-Vue/
├── frontend/          # Vue.js web application
└── backend/           # Node.js server with S7 PLC communication
```

## 🚀 Quick Start

### 1. Start Backend Server

```bash
cd backend
npm run dev
```

The backend will run on `http://localhost:3001`

### 2. Start Frontend Application

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:5173`

### 3. Connect to PLC

1. Open your browser to `http://localhost:5173`
2. Enter your PLC IP address (default: 192.168.190.51)
3. Click "Connect"

## 📋 Features

- ✅ Real-time PLC connection via WebSocket
- ✅ Read/Write DB26 data (8 INT values)
- ✅ Monitor and control marker bits (%M10.0-10.3, %M150.0)
- ✅ Write & Pulse operation (combined write + pulse %M150.0)
- ✅ Live status updates every 500ms
- ✅ Modern, responsive UI

## 🔧 Configuration

### PLC Settings (backend/src/plc/connection.ts)

- **Default IP**: 192.168.190.51
- **Rack**: 0
- **Slot**: 1
- **DB Number**: 26

### Backend Port (backend/src/server.ts)

- **Default**: 3001

### Frontend Backend URL (frontend/src/composables/usePlcClient.ts)

- **Default**: http://localhost:3001

## 📦 Dependencies

### Backend
- `node-snap7` - S7 PLC communication
- `express` - HTTP server
- `socket.io` - WebSocket communication
- `typescript` - Type safety

### Frontend
- `vue` - UI framework
- `socket.io-client` - WebSocket client
- `typescript` - Type safety

## 🛠️ Development

### Backend Scripts
```bash
npm run dev      # Development with auto-reload
npm run start    # Production start
npm run build    # Build TypeScript
```

### Frontend Scripts
```bash
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

## 📝 Notes

- Backend must be running before connecting frontend
- PLC must be accessible on the network
- WebSocket connection required for real-time updates
