import { DB_TAGS, PLC_CONFIG } from './connection';

export class DbOperations {
    private client: any;

    constructor(client: any) {
        this.client = client;
    }

    async readDb(): Promise<number[]> {
        return new Promise((resolve, reject) => {
            this.client.DBRead(
                PLC_CONFIG.DB_NUMBER,
                PLC_CONFIG.START_ADDRESS,
                PLC_CONFIG.SIZE,
                (err: any, data: Buffer) => {
                    if (err) {
                        reject(new Error(`Failed to read DB: ${err}`));
                    } else {
                        const values: number[] = [];
                        for (const tag of DB_TAGS) {
                            const offsetInBuffer = tag.offset - PLC_CONFIG.START_ADDRESS;
                            const value = data.readInt16BE(offsetInBuffer);
                            values.push(value);
                        }
                        resolve(values);
                    }
                }
            );
        });
    }

    async writeDb(values: number[]): Promise<void> {
        if (values.length !== DB_TAGS.length) {
            throw new Error(`Expected ${DB_TAGS.length} values, got ${values.length}`);
        }

        // Validate all values
        for (let i = 0; i < values.length; i++) {
            const value = values[i];
            if (!Number.isInteger(value) || value < -32768 || value > 32767) {
                throw new Error(
                    `${DB_TAGS[i].label}: Value must be an integer between -32768 and 32767 (got ${value})`
                );
            }
        }

        // Read current DB data
        const currentData = await new Promise<Buffer>((resolve, reject) => {
            this.client.DBRead(
                PLC_CONFIG.DB_NUMBER,
                PLC_CONFIG.START_ADDRESS,
                PLC_CONFIG.SIZE,
                (err: any, data: Buffer) => {
                    if (err) reject(new Error(`Failed to read DB: ${err}`));
                    else resolve(data);
                }
            );
        });

        // Modify the buffer
        const buffer = Buffer.from(currentData);
        for (let i = 0; i < values.length; i++) {
            const tag = DB_TAGS[i];
            const offsetInBuffer = tag.offset - PLC_CONFIG.START_ADDRESS;
            buffer.writeInt16BE(values[i], offsetInBuffer);
        }

        // Write back to PLC
        return new Promise((resolve, reject) => {
            this.client.DBWrite(
                PLC_CONFIG.DB_NUMBER,
                PLC_CONFIG.START_ADDRESS,
                PLC_CONFIG.SIZE,
                buffer,
                (err: any) => {
                    if (err) reject(new Error(`Failed to write DB: ${err}`));
                    else resolve();
                }
            );
        });
    }
}
