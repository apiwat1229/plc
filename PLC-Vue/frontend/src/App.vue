<script setup lang="ts">
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ref, watch } from 'vue';
import ControlCenter from './components/ControlCenter.vue';
import LedScoreBoard from './components/LedScoreBoard.vue';

import { useDb54 } from './composables/useDb54';
import { usePlcClient } from './composables/usePlcClient';

// DB26 Client
const {
  connectionStatus: db26Status,
  dbData,
  markerData,
  error: db26Error,
  successMessage: db26Success,
  connectToPlc: connectDb26,
  readDb,
  writeAndPulse,
  writeLineUse,
  writeDb54PoolColor,
  hasData: hasDb26Data,
  isConnected: isDb26SocketConnected,
} = usePlcClient();

// DB54 Client
const {
  isConnected: isDb54Connected,
  isSocketConnected: isLedSocketConnected,
  error: ledError,
  successMessage: ledSuccess,
  connectToPlc: connectDb54,
} = useDb54();

const controlCenterRef = ref<InstanceType<typeof ControlCenter> | null>(null);
const isProcessing = ref(false);

const DEFAULT_PLC_IP_DB26 = '192.168.190.51';
const DEFAULT_PLC_IP_DB54 = '192.168.190.53';

// Auto-connect when socket connects
watch(isDb26SocketConnected, (connected) => {
  if (connected && !db26Status.value.connected) {
    connectDb26(DEFAULT_PLC_IP_DB26);
  }
}, { immediate: true });

watch(isLedSocketConnected, (connected) => {
  if (connected && !isDb54Connected.value) {
    connectDb54(DEFAULT_PLC_IP_DB54);
  }
}, { immediate: true });

const handleWriteAndPulse = async () => {
  if (!controlCenterRef.value) return;
  
  isProcessing.value = true;
  try {
    const values = controlCenterRef.value.getValues();
    writeAndPulse(values);
  } finally {
    setTimeout(() => {
      isProcessing.value = false;
    }, 1000);
  }
};

const handleUpdateLineUse = (bit: number, value: boolean) => {
  // Update PLC Line Status
  writeLineUse(bit, value);

  // Auto-update LED Board Color
  if (dbData.value && hasDb26Data.value) {
    // Line 1 (bit 0) -> dbData index 0 (Pool No)
    // Line 2 (bit 1) -> dbData index 2 (Pool No)
    // Line 3 (bit 2) -> dbData index 4 (Pool No)
    // Line 4 (bit 3) -> dbData index 6 (Pool No)
    const poolDataIndex = bit * 2;
    const poolNo = dbData.value[poolDataIndex] ?? 0;

    // Validate Pool Number (1-23)
    if (poolNo >= 1 && poolNo <= 23) {
      if (value) {
        // Line ON -> Set Pool Color to Green (2)
        console.log(`[Auto] Setting Pool P${poolNo} to GREEN due to Line ${bit + 1} activation`);
        writeDb54PoolColor(poolNo, 2); // 2 = Green
      } else {
        // Line OFF -> Set Pool Color to Yellow (1)
        console.log(`[Auto] Setting Pool P${poolNo} to YELLOW due to Line ${bit + 1} deactivation`);
        writeDb54PoolColor(poolNo, 1); // 1 = Yellow
      }
    } else if (poolNo !== 0) {
      console.warn(`[Auto] Cannot set LED color: Invalid Pool No (${poolNo}) for Line ${bit + 1}`);
    }
  } else {
    console.warn(`[Auto] Cannot set LED color: No DB data available yet for Line ${bit + 1}`);
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 transition-colors duration-500">
    <!-- Sophisticated Industrial Header -->
    <header class="sticky top-0 z-[100] border-b border-slate-200 bg-white/80 backdrop-blur-md px-6 py-4 shadow-sm">
      <div class="mx-auto flex max-w-[1600px] flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-lg shadow-blue-500/20">
            <span class="text-2xl">🏭</span>
          </div>
          <div>
            <h1 class="text-xl font-black tracking-tight text-slate-900 uppercase">PLC Command Center</h1>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Autonomous Monitoring & Control System</p>
          </div>
        </div>

        <!-- Unified Connection Bar -->
        <div class="flex flex-wrap items-center gap-3">
          <!-- DB26 Connection -->
          <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-2 px-4 transition-all hover:bg-slate-50 shadow-sm">
            <div class="flex flex-col">
              <span class="text-[9px] font-black text-slate-400 uppercase">Input Controller (DB26)</span>
              <span class="text-xs font-mono font-bold text-blue-600">{{ DEFAULT_PLC_IP_DB26 }}</span>
            </div>
            <div 
              class="h-3 w-3 rounded-full border-2 border-white transition-all duration-500"
              :class="db26Status.connected ? 'bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.4)] animate-pulse' : 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.4)]'"
            ></div>
          </div>

          <!-- DB54 Connection -->
          <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-2 px-4 transition-all hover:bg-slate-50 shadow-sm">
            <div class="flex flex-col">
              <span class="text-[9px] font-black text-slate-400 uppercase">Display Hub (DB54)</span>
              <span class="text-xs font-mono font-bold text-indigo-600">{{ DEFAULT_PLC_IP_DB54 }}</span>
            </div>
            <div 
              class="h-3 w-3 rounded-full border-2 border-white transition-all duration-500"
              :class="isDb54Connected ? 'bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.4)] animate-pulse' : 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.4)]'"
            ></div>
          </div>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-[1600px] p-6 pt-8">
      <!-- Alerts Area -->
      <div class="mb-6 space-y-2">
         <Alert v-if="db26Error || ledError" variant="destructive" class="border-red-100 bg-red-50 text-red-900 shadow-sm">
          <AlertDescription class="font-bold">❌ {{ db26Error || ledError }}</AlertDescription>
        </Alert>
        <Alert v-if="db26Success || ledSuccess" class="border-green-100 bg-green-50 text-green-900 shadow-sm">
          <AlertDescription class="font-bold">✅ {{ db26Success || ledSuccess }}</AlertDescription>
        </Alert>
      </div>

      <!-- Unified Grid Layout -->
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-12 items-start">
        <!-- Left Column: Controls (Span 4) -->
      <div class="lg:col-span-4 space-y-6">
        <div class="flex items-center justify-between px-2">
          <h2 class="text-sm font-black uppercase tracking-widest text-slate-400">System Inputs</h2>
          <div class="h-px flex-1 bg-gradient-to-r from-slate-200 to-transparent ml-6"></div>
        </div>
        
        <ControlCenter
          ref="controlCenterRef"
          :marker-data="markerData"
          :db-data="dbData"
          :plc-connected="db26Status.connected"
          :has-data="hasDb26Data"
          :is-processing="isProcessing"
          @update-line-use="handleUpdateLineUse"
          @write-and-pulse="handleWriteAndPulse"
          @reload="readDb"
          class="!border-slate-200 !bg-white shadow-sm"
        />
      </div>

      <!-- Right Column: Monitoring (Span 8) -->
      <div class="lg:col-span-8 space-y-6">
        <div class="flex items-center justify-between px-2">
           <h2 class="text-sm font-black uppercase tracking-widest text-slate-400">Global Monitoring</h2>
           <div class="h-px flex-1 bg-gradient-to-r from-slate-200 to-transparent ml-6"></div>
        </div>

          <LedScoreBoard 
            :independent="false" 
          />
        </div>
      </div>
    </main>
  </div>
</template>
