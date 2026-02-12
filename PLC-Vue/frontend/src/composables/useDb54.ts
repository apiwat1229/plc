import { Socket, io } from 'socket.io-client';
import { ref } from 'vue';

const BACKEND_URL = 'http://localhost:3001';

export interface PoolData {
    color: number;  // 0-5
    text: number;   // 0-2
}

export interface DB54Data {
    brightness: number;  // 0-4
    pools: PoolData[];   // P1-P23
}

export interface PoolStatus {
    poolNumber: number;
    value: number;
}

// Color mapping
export const COLOR_OPTIONS = [
    { value: 0, label: 'แดง', color: 'bg-red-500' },
    { value: 1, label: 'เหลือง', color: 'bg-yellow-500' },
    { value: 2, label: 'เขียว', color: 'bg-green-500' },
    { value: 3, label: 'ฟ้า', color: 'bg-sky-400' },
    { value: 4, label: 'น้ำเงิน', color: 'bg-blue-700' },
    { value: 5, label: 'ชมพู', color: 'bg-pink-500' },
];

// Text mapping
export const TEXT_OPTIONS = [
    { value: 0, label: 'EUDR' },
    { value: 1, label: 'FSC' },
    { value: 2, label: 'REG' },
];

// Brightness mapping
export const BRIGHTNESS_OPTIONS = [
    { value: 0, label: '0%' },
    { value: 1, label: '25%' },
    { value: 2, label: '50%' },
    { value: 3, label: '75%' },
    { value: 4, label: '100%' },
];

// Shared state
const socket = ref<Socket | null>(null);
const isSocketConnected = ref(false);
const isConnected = ref(false); // PLC connection

// DB54 data
const brightness = ref(0);
const pools = ref<PoolData[]>(
    Array.from({ length: 23 }, () => ({ color: 0, text: 0 }))
);

// Real-time pool status
const poolStatus = ref<PoolStatus[]>(
    Array.from({ length: 23 }, (_, i) => ({ poolNumber: i + 1, value: 0 }))
);
const sentData = ref(false);

// UI state
const error = ref<string | null>(null);
const successMessage = ref<string | null>(null);
const isLoading = ref(false);
const hasData = ref(false);

export function useDb54() {

    // Initialize socket connection
    const connect = () => {
        socket.value = io(BACKEND_URL);

        socket.value.on('connect', () => {
            console.log('Connected to backend for DB54');
            isSocketConnected.value = true;
        });

        socket.value.on('disconnect', () => {
            console.log('Disconnected from backend');
            isSocketConnected.value = false;
            isConnected.value = false;
            hasData.value = false;
        });

        // Connection status
        socket.value.on('plc-connection-status', (data: { connected: boolean }) => {
            isConnected.value = data.connected;
            if (data.connected) {
                readDB54(); // Auto-reload on connect
            } else {
                hasData.value = false;
            }
        });

        // DB54 data received
        socket.value.on('db54-data', (data: DB54Data) => {
            brightness.value = data.brightness;
            pools.value = data.pools;
            isLoading.value = false;
            hasData.value = true;
        });

        // Pool status updates (real-time)
        socket.value.on('db54-pool-status', (data: { pools: PoolStatus[]; sentData: boolean }) => {
            poolStatus.value = data.pools;
            sentData.value = data.sentData;
        });

        // Write success
        socket.value.on('db54-write-success', (data: { message: string }) => {
            successMessage.value = data.message;
            readDB54(); // Auto-reload after write
            setTimeout(() => {
                successMessage.value = null;
            }, 3000);
            isLoading.value = false;
        });

        // Error handling
        socket.value.on('plc-error', (data: { message: string }) => {
            error.value = data.message;
            setTimeout(() => {
                error.value = null;
            }, 5000);
            isLoading.value = false;
            hasData.value = false;
        });
    };

    // Connect to PLC
    const connectToPlc = (ip: string) => {
        if (!socket.value) return;
        socket.value.emit('plc-connect-db54', { ip });
    };

    // Disconnect from PLC
    const disconnectFromPlc = () => {
        if (!socket.value) return;
        socket.value.emit('plc-disconnect-db54');
        hasData.value = false;
    };

    // Read DB54
    const readDB54 = () => {
        if (!socket.value) return;
        isLoading.value = true;
        socket.value.emit('db54-read');
    };

    // Write DB54 and pulse M150.0
    const writeAndPulse = () => {
        if (!socket.value) return;
        isLoading.value = true;

        const data: DB54Data = {
            brightness: brightness.value,
            pools: pools.value,
        };

        socket.value.emit('db54-write-and-pulse', data);
    };

    // Update pool color
    const updatePoolColor = (poolIndex: number, color: number) => {
        const pool = pools.value[poolIndex];
        if (pool) {
            pools.value[poolIndex] = { ...pool, color };
        }
    };

    // Update pool text
    const updatePoolText = (poolIndex: number, text: number) => {
        const pool = pools.value[poolIndex];
        if (pool) {
            pools.value[poolIndex] = { ...pool, text };
        }
    };

    // Update brightness
    const updateBrightness = (value: number) => {
        brightness.value = value;
    };

    // Reset all pools
    const resetAll = () => {
        brightness.value = 0;
        pools.value = Array.from({ length: 23 }, () => ({ color: 0, text: 0 }));
        hasData.value = false;
    };

    // Get pool status value
    const getPoolStatusValue = (poolNumber: number): number | string => {
        if (!hasData.value) return '-';
        const status = poolStatus.value.find(p => p.poolNumber === poolNumber);
        return status ? status.value : 0;
    };

    // Get color option by value
    const getColorOption = (value: number) => {
        return COLOR_OPTIONS.find(opt => opt.value === value) || COLOR_OPTIONS[0];
    };

    // Get text option by value
    const getTextOption = (value: number) => {
        return TEXT_OPTIONS.find(opt => opt.value === value) || TEXT_OPTIONS[0];
    };

    // Initialize on first use if not already done
    if (!socket.value) {
        connect();
    }

    return {
        // State
        isConnected,
        isSocketConnected,
        brightness,
        pools,
        poolStatus,
        sentData,
        error,
        successMessage,
        isLoading,
        hasData,

        // Actions
        connectToPlc,
        disconnectFromPlc,
        readDB54,
        writeAndPulse,
        updatePoolColor,
        updatePoolText,
        updateBrightness,
        resetAll,

        // Helpers
        getPoolStatusValue,
        getColorOption,
        getTextOption,

        // Constants
        COLOR_OPTIONS,
        TEXT_OPTIONS,
        BRIGHTNESS_OPTIONS,
    };
}
