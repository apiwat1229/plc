declare module 'node-snap7' {
    export class S7Client {
        constructor();
        ConnectTo(ip: string, rack: number, slot: number, callback: (err: number | null) => void): void;
        Disconnect(): void;

        // Callback-based methods
        DBRead(dbNumber: number, start: number, size: number, callback: (err: number | null, data: Buffer) => void): void;
        DBWrite(dbNumber: number, start: number, buffer: Buffer, callback: (err: number | null) => void): void;
        MBRead(start: number, size: number, callback: (err: number | null, data: Buffer) => void): void;
        MBWrite(start: number, size: number, buffer: Buffer, callback: (err: number | null) => void): void;

        // Promise-based methods (overloads)
        DBRead(dbNumber: number, start: number, size: number): Promise<Buffer>;
        DBWrite(dbNumber: number, start: number, size: number, buffer: Buffer): Promise<void>;
        MBRead(start: number, size: number): Promise<Buffer>;
        MBWrite(start: number, size: number, buffer: Buffer): Promise<void>;
    }

    export interface Util {
        GetIntAt(buffer: Buffer, offset: number): number;
        SetIntAt(buffer: Buffer, offset: number, value: number): void;
        GetBitAt(buffer: Buffer, byteOffset: number, bitOffset: number): boolean;
        SetBitAt(buffer: Buffer, byteOffset: number, bitOffset: number, value: boolean): void;
    }

    export const util: Util;

    export namespace client {
        class Client extends S7Client {
            constructor();
        }
    }
}
