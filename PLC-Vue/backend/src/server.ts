import cors from 'cors';
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { PlcConnection } from './plc/connection';
import { DbOperations } from './plc/db-operations';
import { DB54Operations } from './plc/db54-operations';
import { MarkerOperations } from './plc/marker-operations';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST'],
    },
});

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;

// PLC Connection and Operations for DB26
const plcConnection = new PlcConnection();
let dbOps: DbOperations | null = null;
let markerOps: MarkerOperations | null = null;

// Separate PLC Connection for DB54 (LED Board)
const plcConnectionDB54 = new PlcConnection();
let db54Ops: DB54Operations | null = null;

let pollingInterval: NodeJS.Timeout | null = null;
let poolStatusInterval: NodeJS.Timeout | null = null;

// Socket.IO event handlers
io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);

    // Send current connection status
    socket.emit('connection-status', plcConnection.getConnectionStatus());

    // If already connected (e.g. page refresh), send data and start polling immediately
    if (plcConnection.isClientConnected() && dbOps && markerOps) {
        console.log('Client reconnected to existing PLC session');
        dbOps.readDb().then(data => socket.emit('db-data', data)).catch(console.error);
        markerOps.readMarkers().then(data => socket.emit('marker-data', data)).catch(console.error);
        startPolling(socket);
        socket.emit('plc-connected', { success: true });
    }

    // If DB54 is already connected
    if (plcConnectionDB54.isClientConnected() && db54Ops) {
        console.log('Client reconnected to existing DB54 session');
        db54Ops.readDB54().then(data => socket.emit('db54-data', data)).catch(console.error);
        startPoolStatusPolling(socket);
        socket.emit('plc-connection-status', { connected: true });
    }

    // Connect to PLC (DB26)
    socket.on('plc-connect', async (ip: string) => {
        try {
            await plcConnection.connect(ip);
            const client = plcConnection.getClient();
            dbOps = new DbOperations(client);
            markerOps = new MarkerOperations(client);

            socket.emit('connection-status', plcConnection.getConnectionStatus());
            socket.emit('plc-connected', { success: true });

            // Start polling
            startPolling(socket);
            startPoolStatusPolling(socket);

            // Initial data read
            const dbData = await dbOps.readDb();
            const markers = await markerOps.readMarkers();
            socket.emit('db-data', dbData);
            socket.emit('marker-data', markers);
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
            socket.emit('plc-connected', { success: false, error: error.message });
        }
    });

    // Disconnect from PLC
    socket.on('plc-disconnect', async () => {
        try {
            stopPolling();
            await plcConnection.disconnect();
            dbOps = null;
            markerOps = null;
            socket.emit('connection-status', plcConnection.getConnectionStatus());
            socket.emit('plc-disconnected', { success: true });
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
        }
    });

    // Read DB
    socket.on('read-db', async () => {
        if (!dbOps || !markerOps) {
            socket.emit('plc-error', { message: 'PLC not connected' });
            return;
        }
        try {
            const data = await dbOps.readDb();
            const markers = await markerOps.readMarkers();
            socket.emit('db-data', data);
            socket.emit('marker-data', markers);
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
        }
    });

    // Write DB and Pulse
    socket.on('write-and-pulse', async (values: number[]) => {
        if (!dbOps || !markerOps) {
            socket.emit('plc-error', { message: 'PLC not connected' });
            return;
        }
        try {
            await dbOps.writeDb(values);
            await markerOps.pulseSentData();
            socket.emit('write-success', { message: 'Wrote to DB and Pulsed %M150.0 successfully.' });
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
        }
    });

    // Write Line Use Bit
    socket.on('write-line-use', async ({ bit, value }: { bit: number; value: boolean }) => {
        if (!markerOps) {
            socket.emit('plc-error', { message: 'PLC not connected' });
            return;
        }
        try {
            await markerOps.writeLineUseBit(bit, value);
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
        }
    });

    // DB54 Operations - LED Score Board
    socket.on('db54-read', async () => {
        console.log('[DB54] Read request received, db54Ops exists:', !!db54Ops);
        if (!db54Ops) {
            console.error('[DB54] Read failed: PLC not connected');
            socket.emit('plc-error', { message: 'PLC not connected' });
            return;
        }
        try {
            console.log('[DB54] Attempting to read DB54...');
            const data = await db54Ops.readDB54();
            console.log('[DB54] Read success! Brightness:', data.brightness, 'Pools:', data.pools.length);
            console.log('[DB54] First 3 pools:', JSON.stringify(data.pools.slice(0, 3)));
            socket.emit('db54-data', data);
        } catch (error: any) {
            console.error('[DB54] Read error:', error.message, error.stack);
            socket.emit('plc-error', { message: error.message });
        }
    });

    socket.on('db54-write-and-pulse', async (data: any) => {
        console.log('[DB54] Write request received, db54Ops exists:', !!db54Ops);
        if (!db54Ops) {
            console.error('[DB54] Write failed: PLC not connected');
            socket.emit('plc-error', { message: 'PLC not connected' });
            return;
        }
        try {
            console.log('[DB54] Writing data:', JSON.stringify(data).substring(0, 200));
            await db54Ops.writeDB54(data);
            await db54Ops.pulseMarker();
            console.log('[DB54] Write and pulse successful');
            socket.emit('db54-write-success', { message: 'Wrote DB54 and pulsed %M150.0' });
        } catch (error: any) {
            console.error('[DB54] Write error:', error.message);
            socket.emit('plc-error', { message: error.message });
        }
    });

    socket.on('write-db54-pool-color', async (data: { poolIndex: number; color: number }) => {
        if (!db54Ops) {
            socket.emit('plc-error', { message: 'PLC not connected' });
            return;
        }
        try {
            await db54Ops.writePoolColor(data.poolIndex, data.color);
            socket.emit('db54-write-success', { message: `Updated Pool P${data.poolIndex} Color` });
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
        }
    });

    // DB54 PLC Connection (separate from DB26)
    socket.on('plc-connect-db54', async (data: { ip: string }) => {
        console.log('[DB54] Connection request to IP:', data.ip);
        try {
            await plcConnectionDB54.connect(data.ip);
            const client = plcConnectionDB54.getClient();
            db54Ops = new DB54Operations(client);
            console.log('[DB54] Connected successfully, db54Ops created');

            socket.emit('plc-connection-status', { connected: true });

            // Start pool status polling for DB54
            startPoolStatusPolling(socket);
        } catch (error: any) {
            console.error('[DB54] Connection error:', error.message);
            socket.emit('plc-error', { message: error.message });
            socket.emit('plc-connection-status', { connected: false });
        }
    });

    socket.on('plc-disconnect-db54', async () => {
        try {
            stopPoolStatusPolling();
            await plcConnectionDB54.disconnect();
            db54Ops = null;
            socket.emit('plc-connection-status', { connected: false });
        } catch (error: any) {
            socket.emit('plc-error', { message: error.message });
        }
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
        stopPoolStatusPolling();
    });
});

// Polling function
function startPolling(socket: any) {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    pollingInterval = setInterval(async () => {
        if (!plcConnection.isClientConnected() || !markerOps) {
            stopPolling();
            return;
        }

        try {
            const markers = await markerOps.readMarkers();
            socket.emit('marker-data', markers);
        } catch (error: any) {
            console.error('Polling error:', error.message);
            stopPolling();
            await plcConnection.disconnect();
            socket.emit('connection-status', plcConnection.getConnectionStatus());
            socket.emit('plc-error', { message: 'Connection lost' });
        }
    }, 500);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// Pool status polling for DB54
function startPoolStatusPolling(socket: any) {
    if (poolStatusInterval) {
        clearInterval(poolStatusInterval);
    }

    poolStatusInterval = setInterval(async () => {
        if (!plcConnectionDB54.isClientConnected() || !db54Ops) {
            stopPoolStatusPolling();
            return;
        }

        try {
            const poolStatus = await db54Ops.readPoolStatus();
            const sentData = await db54Ops.readSentDataMarker();
            socket.emit('db54-pool-status', { pools: poolStatus, sentData });
        } catch (error: any) {
            // Silently handle errors when PLC is not physically connected
            // This prevents console spam when testing without real PLC
            if (error.message && !error.message.includes('undefined')) {
                console.error('Pool status polling error:', error.message);
            }
        }
    }, 500);
}

function stopPoolStatusPolling() {
    if (poolStatusInterval) {
        clearInterval(poolStatusInterval);
        poolStatusInterval = null;
    }
}

// Start server
httpServer.listen(PORT, () => {
    console.log(`🚀 Backend server running on http://localhost:${PORT}`);
    console.log(`📡 WebSocket server ready for connections`);
});
