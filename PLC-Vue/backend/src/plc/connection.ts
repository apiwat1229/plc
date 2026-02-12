import snap7 from 'node-snap7';

// PLC Configuration
export const PLC_CONFIG = {
    DEFAULT_IP: '192.168.190.51',
    RACK: 0,
    SLOT: 1,
    DB_NUMBER: 26,
    START_ADDRESS: 0,
    SIZE: 32,
    M_BASE_LINE_USE: 10,
    M_BASE_SENT_DATA: 150,
};

// DB Tags Configuration
export const DB_TAGS = [
    { label: 'Data_Center[1]', desc: 'หมายเลขบ่อ บรรทัดที่ 1', offset: 2 },
    { label: 'Data_Center[3]', desc: 'จำนวนตัก บรรทัดที่ 1', offset: 6 },
    { label: 'Data_Center[5]', desc: 'หมายเลขบ่อ บรรทัดที่ 2', offset: 10 },
    { label: 'Data_Center[7]', desc: 'จำนวนตัก บรรทัดที่ 2', offset: 14 },
    { label: 'Data_Center[9]', desc: 'หมายเลขบ่อ บรรทัดที่ 3', offset: 18 },
    { label: 'Data_Center[11]', desc: 'จำนวนตัก บรรทัดที่ 3', offset: 22 },
    { label: 'Data_Center[13]', desc: 'หมายเลขบ่อ บรรทัดที่ 4', offset: 26 },
    { label: 'Data_Center[15]', desc: 'จำนวนตัก บรรทัดที่ 4', offset: 30 },
];

// Marker Bit Positions
export const MARKER_BITS = {
    SENT_DATA: 0,
    LINE1_USE: 0,
    LINE2_USE: 1,
    LINE3_USE: 2,
    LINE4_USE: 3,
};

export class PlcConnection {
    private client: any;
    private isConnected: boolean = false;
    private currentIp: string = '';

    constructor() {
        this.client = new snap7.S7Client();
    }

    async connect(ip: string): Promise<void> {
        console.log(`[PLC] Attempting to connect to ${ip}, Rack: ${PLC_CONFIG.RACK}, Slot: ${PLC_CONFIG.SLOT}`);

        if (this.isConnected) {
            console.log('[PLC] Already connected, disconnecting first...');
            await this.disconnect();
        }

        return new Promise((resolve, reject) => {
            console.log('[PLC] Calling ConnectTo...');
            this.client.ConnectTo(ip, PLC_CONFIG.RACK, PLC_CONFIG.SLOT, (err: any) => {
                if (err) {
                    this.isConnected = false;
                    console.error(`[PLC] Connection failed - Error code: ${err}, Type: ${typeof err}`);
                    console.error(`[PLC] Full error object:`, JSON.stringify(err));

                    // Provide more helpful error message
                    let errorMessage = `Failed to connect to PLC at ${ip}`;
                    if (err === 51) {
                        errorMessage += ` (Error 51: Connection refused - Check if PLC is online, IP is correct, and PUT/GET is enabled)`;
                    } else {
                        errorMessage += ` (Error code: ${err})`;
                    }

                    reject(new Error(errorMessage));
                } else {
                    this.isConnected = true;
                    this.currentIp = ip;
                    console.log(`[PLC] Successfully connected to ${ip}`);
                    resolve();
                }
            });
        });
    }

    async disconnect(): Promise<void> {
        if (!this.isConnected) return;

        return new Promise((resolve) => {
            this.client.Disconnect();
            this.isConnected = false;
            this.currentIp = '';
            resolve();
        });
    }

    getConnectionStatus(): { connected: boolean; ip: string } {
        return {
            connected: this.isConnected,
            ip: this.currentIp,
        };
    }

    getClient(): any {
        if (!this.isConnected) {
            throw new Error('PLC is not connected');
        }
        return this.client;
    }

    isClientConnected(): boolean {
        return this.isConnected;
    }
}
