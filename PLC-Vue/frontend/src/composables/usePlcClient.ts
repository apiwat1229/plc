import { Socket, io } from 'socket.io-client';
import { ref } from 'vue';

const BACKEND_URL = 'http://localhost:3001';

export interface MarkerState {
    sentData: boolean;
    line1Use: boolean;
    line2Use: boolean;
    line3Use: boolean;
    line4Use: boolean;
}

export interface ConnectionStatus {
    connected: boolean;
    ip: string;
}

// Shared state
const socket = ref<Socket | null>(null);
const isConnected = ref(false);
const connectionStatus = ref<ConnectionStatus>({ connected: false, ip: '' });
const dbData = ref<number[]>([0, 0, 0, 0, 0, 0, 0, 0]);
const markerData = ref<MarkerState>({
    sentData: false,
    line1Use: false,
    line2Use: false,
    line3Use: false,
    line4Use: false,
});
const error = ref<string>('');
const successMessage = ref<string>('');
const hasData = ref(false);

export function usePlcClient() {

    const connect = () => {
        if (socket.value) return;

        socket.value = io(BACKEND_URL);

        socket.value.on('connect', () => {
            isConnected.value = true;
            console.log('Connected to backend');
        });

        socket.value.on('disconnect', () => {
            isConnected.value = false;
            connectionStatus.value = { connected: false, ip: '' };
            hasData.value = false;
            console.log('Disconnected from backend');
        });

        socket.value.on('connection-status', (status: ConnectionStatus) => {
            connectionStatus.value = status;
            if (!status.connected) {
                hasData.value = false;
            }
        });

        socket.value.on('db-data', (data: number[]) => {
            dbData.value = data;
            hasData.value = true;
        });

        socket.value.on('marker-data', (data: MarkerState) => {
            markerData.value = data;
        });

        socket.value.on('plc-error', (data: { message: string }) => {
            error.value = data.message;
            setTimeout(() => (error.value = ''), 5000);
        });

        socket.value.on('write-success', (data: { message: string }) => {
            successMessage.value = data.message;
            readDb(); // Auto-reload after write
            setTimeout(() => (successMessage.value = ''), 3000);
        });

        socket.value.on('plc-connected', (data: { success: boolean; error?: string }) => {
            if (data.success) {
                readDb(); // Auto-reload on connect
            } else if (data.error) {
                error.value = data.error;
                hasData.value = false;
                setTimeout(() => (error.value = ''), 5000);
            }
        });
    };


    const connectToPlc = (ip: string) => {
        if (!socket.value) return;
        socket.value.emit('plc-connect', ip);
    };

    const disconnectFromPlc = () => {
        if (!socket.value) return;
        socket.value.emit('plc-disconnect');
        hasData.value = false;
    };

    const readDb = () => {
        if (!socket.value) return;
        socket.value.emit('read-db');
    };

    const writeAndPulse = (values: number[]) => {
        if (!socket.value) return;
        socket.value.emit('write-and-pulse', values);
    };

    const writeLineUse = (bit: number, value: boolean) => {
        // Optimistic update
        const key = `line${bit + 1}Use` as keyof MarkerState;
        markerData.value[key] = value;

        if (!socket.value) return;
        socket.value.emit('write-line-use', { bit, value });
    };

    const writeDb54PoolColor = (poolIndex: number, color: number) => {
        if (!socket.value) return;
        console.log(`Sending write-db54-pool-color: Pool ${poolIndex}, Color ${color}`);
        socket.value.emit('write-db54-pool-color', { poolIndex, color });
    };

    // Initialize on first use if not already done
    if (!socket.value) {
        connect();
    }

    return {
        isConnected,
        connectionStatus,
        dbData,
        markerData,
        error,
        successMessage,
        hasData,
        connectToPlc,
        disconnectFromPlc,
        readDb,
        writeAndPulse,
        writeLineUse,
        writeDb54PoolColor,
    };
}
