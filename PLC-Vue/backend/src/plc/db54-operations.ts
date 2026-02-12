import snap7 from 'node-snap7';

export interface PoolData {
    color: number;  // 0-5: Red, Yellow, Green, Cyan, Blue, Pink
    text: number;   // 0-2: EUDR, FSC, REG
}

export interface DB54Data {
    brightness: number;  // 0-4: 0%, 25%, 50%, 75%, 100%
    pools: PoolData[];   // P1-P23 (23 pools)
}

export interface PoolStatus {
    poolNumber: number;  // 1-23
    value: number;       // Current value from DB(n).DBW18
}

const DB_NUMBER = 54;
const START_ADDRESS = 0;
const SIZE = 94;  // Total bytes for DB54

// Marker for SENT_DATA
const M_BASE_SENT_DATA = 150;
const M_SENT_DATA_BIT = 0;

export class DB54Operations {
    constructor(private client: snap7.S7Client) { }

    /**
     * Read entire DB54 data
     */
    async readDB54(): Promise<DB54Data> {
        console.log('[DB54Ops] === Starting DB54 Read ===');
        console.log('[DB54Ops] Reading from DB', DB_NUMBER, 'Address:', START_ADDRESS, 'Size:', SIZE);

        const buffer = await this.client.DBRead(DB_NUMBER, START_ADDRESS, SIZE);
        console.log('[DB54Ops] Buffer received:');
        console.log('[DB54Ops]   - Type:', typeof buffer);
        console.log('[DB54Ops]   - Length:', buffer?.length);
        console.log('[DB54Ops]   - Is Buffer:', Buffer.isBuffer(buffer));
        console.log('[DB54Ops]   - First 20 bytes:', buffer ? Array.from(buffer.slice(0, 20)) : 'null');

        if (!buffer) {
            throw new Error('Buffer is null or undefined');
        }

        // Read brightness (DBW0)
        // util.GetIntAt(buffer, 0)
        const brightness = buffer.readInt16BE(0);
        console.log('[DB54Ops] Brightness (offset 0):', brightness);

        // Read 23 pools (P1-P23)
        const pools: PoolData[] = [];
        for (let i = 0; i < 23; i++) {
            const colorOffset = 2 + (i * 4);      // DBW2, DBW6, DBW10, ...
            const textOffset = 2 + (i * 4) + 2;   // DBW4, DBW8, DBW12, ...

            const colorValue = buffer.readInt16BE(colorOffset);
            const textValue = buffer.readInt16BE(textOffset);

            // Log first 3 pools in detail
            if (i < 3) {
                console.log(`[DB54Ops] P${i + 1}:`);
                console.log(`[DB54Ops]   - colorOffset=${colorOffset}, bytes at offset: [${buffer[colorOffset]}, ${buffer[colorOffset + 1]}], value=${colorValue}`);
                console.log(`[DB54Ops]   - textOffset=${textOffset}, bytes at offset: [${buffer[textOffset]}, ${buffer[textOffset + 1]}], value=${textValue}`);
            }

            pools.push({
                color: colorValue,
                text: textValue,
            });
        }

        console.log('[DB54Ops] Total pools read:', pools.length);
        console.log('[DB54Ops] === DB54 Read Complete ===');

        return { brightness, pools };
    }

    /**
     * Write entire DB54 data
     */
    async writeDB54(data: DB54Data): Promise<void> {
        // Read current buffer first
        const rawBuffer = await this.client.DBRead(DB_NUMBER, START_ADDRESS, SIZE);
        if (!rawBuffer) throw new Error('Failed to read DB54 buffer for writing');

        const buffer = Buffer.from(rawBuffer);

        // Write brightness (DBW0)
        buffer.writeInt16BE(data.brightness, 0);

        // Write 23 pools
        for (let i = 0; i < 23; i++) {
            const colorOffset = 2 + (i * 4);
            const textOffset = 2 + (i * 4) + 2;

            if (data.pools[i]) {
                buffer.writeInt16BE(data.pools[i].color, colorOffset);
                buffer.writeInt16BE(data.pools[i].text, textOffset);
            }
        }

        // Write back to PLC
        await this.client.DBWrite(DB_NUMBER, START_ADDRESS, SIZE, buffer);
    }

    /**
     * Write specific pool color
     * @param poolIndex 1-based index (1-23)
     * @param color 0-5 (Red, Yellow, Green, Cyan, Blue, Pink)
     */
    async writePoolColor(poolIndex: number, color: number): Promise<void> {
        if (poolIndex < 1 || poolIndex > 23) {
            throw new Error(`Invalid pool index: ${poolIndex}. Must be 1-23.`);
        }

        // Read current buffer
        const rawBuffer = await this.client.DBRead(DB_NUMBER, START_ADDRESS, SIZE);
        if (!rawBuffer) throw new Error('Failed to read DB54 buffer for color update');

        const buffer = Buffer.from(rawBuffer);

        // Calculate offset for color (P1 Color is at offset 2)
        // P1: 2 + (0 * 4) = 2
        // P2: 2 + (1 * 4) = 6
        const colorOffset = 2 + ((poolIndex - 1) * 4);

        console.log(`[DB54Ops] Writing Color ${color} to Pool P${poolIndex} at offset ${colorOffset}`);

        // Update color
        buffer.writeInt16BE(color, colorOffset);

        // Write back to PLC
        await this.client.DBWrite(DB_NUMBER, START_ADDRESS, SIZE, buffer);

        // Pulse marker to notify change
        await this.pulseMarker();
    }

    /**
     * Pulse M150.0 marker for ~500ms
     */
    async pulseMarker(): Promise<void> {
        // Read current marker state
        let rawBuffer = await this.client.MBRead(M_BASE_SENT_DATA, 1);
        if (!rawBuffer) throw new Error('Failed to read M150.0');

        let buffer = Buffer.from(rawBuffer);

        // Set M150.0 to true
        // util.SetBitAt(buffer, 0, M_SENT_DATA_BIT, true)
        buffer[0] |= (1 << M_SENT_DATA_BIT);
        await this.client.MBWrite(M_BASE_SENT_DATA, 1, buffer);

        // Wait 500ms
        await new Promise(resolve => setTimeout(resolve, 500));

        // Set M150.0 to false
        rawBuffer = await this.client.MBRead(M_BASE_SENT_DATA, 1);
        if (rawBuffer) {
            buffer = Buffer.from(rawBuffer);
            // util.SetBitAt(buffer, 0, M_SENT_DATA_BIT, false)
            buffer[0] &= ~(1 << M_SENT_DATA_BIT);
            await this.client.MBWrite(M_BASE_SENT_DATA, 1, buffer);
        }
    }

    /**
     * Read pool status from DB2-DB24 (DBW18)
     * P1 = DB2.DBW18, P2 = DB3.DBW18, ..., P23 = DB24.DBW18
     */
    async readPoolStatus(): Promise<PoolStatus[]> {
        const statuses: PoolStatus[] = [];

        for (let i = 1; i <= 23; i++) {
            const dbNumber = i + 1;  // DB2 for P1, DB3 for P2, ..., DB24 for P23
            const address = 18;
            const size = 2;

            try {
                const buffer = await this.client.DBRead(dbNumber, address, size);

                if (!buffer || !Buffer.isBuffer(buffer)) {
                    // console.warn(`Pool P${i}: Buffer is null or invalid`);
                    statuses.push({
                        poolNumber: i,
                        value: 0,
                    });
                    continue;
                }

                const value = buffer.readInt16BE(0);

                statuses.push({
                    poolNumber: i,
                    value,
                });
            } catch (error) {
                // console.error(`Error reading pool P${i} status:`, error);
                statuses.push({
                    poolNumber: i,
                    value: 0,
                });
            }
        }

        return statuses;
    }

    /**
     * Read SENT_DATA marker (M150.0)
     */
    async readSentDataMarker(): Promise<boolean> {
        const buffer = await this.client.MBRead(M_BASE_SENT_DATA, 1);
        // util.GetBitAt(buffer, 0, M_SENT_DATA_BIT)
        return (buffer[0] & (1 << M_SENT_DATA_BIT)) !== 0;
    }
}
