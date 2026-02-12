import { MARKER_BITS, PLC_CONFIG } from './connection';

export interface MarkerState {
    sentData: boolean;
    line1Use: boolean;
    line2Use: boolean;
    line3Use: boolean;
    line4Use: boolean;
}

export class MarkerOperations {
    private client: any;

    constructor(client: any) {
        this.client = client;
    }

    async readMarkers(): Promise<MarkerState> {
        const lineUseData = await this.readMarkerByte(PLC_CONFIG.M_BASE_LINE_USE);
        const sentDataData = await this.readMarkerByte(PLC_CONFIG.M_BASE_SENT_DATA);

        return {
            sentData: this.getBit(sentDataData, MARKER_BITS.SENT_DATA),
            line1Use: this.getBit(lineUseData, MARKER_BITS.LINE1_USE),
            line2Use: this.getBit(lineUseData, MARKER_BITS.LINE2_USE),
            line3Use: this.getBit(lineUseData, MARKER_BITS.LINE3_USE),
            line4Use: this.getBit(lineUseData, MARKER_BITS.LINE4_USE),
        };
    }

    async writeLineUseBit(bitPosition: number, value: boolean): Promise<void> {
        const data = await this.readMarkerByte(PLC_CONFIG.M_BASE_LINE_USE);
        const newData = this.setBit(data, bitPosition, value);
        await this.writeMarkerByte(PLC_CONFIG.M_BASE_LINE_USE, newData);
    }

    async pulseSentData(): Promise<void> {
        // Set bit to true
        const data = await this.readMarkerByte(PLC_CONFIG.M_BASE_SENT_DATA);
        const onData = this.setBit(data, MARKER_BITS.SENT_DATA, true);
        await this.writeMarkerByte(PLC_CONFIG.M_BASE_SENT_DATA, onData);

        // Wait 500ms
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Set bit to false
        const data2 = await this.readMarkerByte(PLC_CONFIG.M_BASE_SENT_DATA);
        const offData = this.setBit(data2, MARKER_BITS.SENT_DATA, false);
        await this.writeMarkerByte(PLC_CONFIG.M_BASE_SENT_DATA, offData);
    }

    private readMarkerByte(markerBase: number): Promise<Buffer> {
        return new Promise((resolve, reject) => {
            this.client.MBRead(markerBase, 1, (err: any, data: Buffer) => {
                if (err) reject(new Error(`Failed to read marker: ${err}`));
                else resolve(data);
            });
        });
    }

    private writeMarkerByte(markerBase: number, data: Buffer): Promise<void> {
        return new Promise((resolve, reject) => {
            this.client.MBWrite(markerBase, 1, data, (err: any) => {
                if (err) reject(new Error(`Failed to write marker: ${err}`));
                else resolve();
            });
        });
    }

    private getBit(buffer: Buffer, bitPosition: number): boolean {
        const byte = buffer[0];
        return ((byte >> bitPosition) & 1) === 1;
    }

    private setBit(buffer: Buffer, bitPosition: number, value: boolean): Buffer {
        const newBuffer = Buffer.from(buffer);
        if (value) {
            newBuffer[0] |= 1 << bitPosition;
        } else {
            newBuffer[0] &= ~(1 << bitPosition);
        }
        return newBuffer;
    }
}
