<script setup lang="ts">
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Activity,
  Cpu,
  Factory,
  Info,
  Layers,
  Wifi,
  WifiOff,
} from "lucide-vue-next";
import { ref, watch } from "vue";
import ControlCenter from "./components/ControlCenter.vue";
import LedScoreBoard from "./components/LedScoreBoard.vue";

import { useDb54 } from "./composables/useDb54";
import { usePlcClient } from "./composables/usePlcClient";

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

const DEFAULT_PLC_IP_DB26 = "192.168.190.51";
const DEFAULT_PLC_IP_DB54 = "192.168.190.53";

// Auto-connect when socket connects
watch(
  isDb26SocketConnected,
  (connected) => {
    if (connected && !db26Status.value.connected) {
      connectDb26(DEFAULT_PLC_IP_DB26);
    }
  },
  { immediate: true },
);

watch(
  isLedSocketConnected,
  (connected) => {
    if (connected && !isDb54Connected.value) {
      connectDb54(DEFAULT_PLC_IP_DB54);
    }
  },
  { immediate: true },
);

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
    const poolDataIndex = bit * 2;
    const poolNo = dbData.value[poolDataIndex] ?? 0;

    if (poolNo >= 1 && poolNo <= 23) {
      if (value) {
        writeDb54PoolColor(poolNo, 2); // 2 = Green
      } else {
        writeDb54PoolColor(poolNo, 1); // 1 = Yellow
      }
    }
  }
};
</script>

<template>
  <div
    class="min-h-screen bg-background text-foreground transition-colors duration-500 grid-bg"
  >
    <!-- Sophisticated Industrial Header -->
    <header class="sticky top-0 z-[100] glass-header px-6 py-4">
      <div
        class="mx-auto flex max-w-[1700px] flex-col gap-4 md:flex-row md:items-center md:justify-between"
      >
        <div class="flex items-center gap-5">
          <div
            class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-secondary border border-black/10"
          >
            <Factory class="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1
              class="text-2xl font-black tracking-tight uppercase leading-none italic"
            >
              <span class="text-primary">PLC</span> COMMAND CENTER
            </h1>
            <p
              class="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.3em] mt-1 flex items-center gap-2"
            >
              <Activity class="h-3 w-3 text-primary animate-pulse" />
              Autonomous Monitoring & Control System
            </p>
          </div>
        </div>

        <!-- Unified Connection Bar -->
        <div class="flex flex-wrap items-center gap-4">
          <!-- DB26 Connection -->
          <div
            class="flex items-center gap-4 glass-card p-2 px-5 rounded-2xl border-black/10 tech-border"
          >
            <div class="p-2 rounded-xl bg-primary/5">
              <Cpu class="h-5 w-5 text-primary" />
            </div>
            <div class="flex flex-col min-w-[120px]">
              <span
                class="text-[10px] font-black text-muted-foreground uppercase tracking-widest"
                >Input Master</span
              >
              <span class="text-xs font-mono font-bold">{{
                DEFAULT_PLC_IP_DB26
              }}</span>
            </div>
            <div class="relative flex items-center justify-center">
              <div
                class="h-3 w-3 rounded-full transition-all duration-500 relative z-10"
                :class="db26Status.connected ? 'bg-green-500' : 'bg-red-500'"
              ></div>
              <div
                v-if="db26Status.connected"
                class="absolute h-5 w-5 rounded-full bg-green-500/10 animate-ping"
              ></div>
            </div>
          </div>

          <!-- DB54 Connection -->
          <div
            class="flex items-center gap-4 glass-card p-2 px-5 rounded-2xl border-black/10 tech-border"
          >
            <div class="p-2 rounded-xl bg-secondary/5">
              <Layers class="h-5 w-5 text-secondary" />
            </div>
            <div class="flex flex-col min-w-[120px]">
              <span
                class="text-[10px] font-black text-muted-foreground uppercase tracking-widest"
                >Display Hub</span
              >
              <span class="text-xs font-mono font-bold">{{
                DEFAULT_PLC_IP_DB54
              }}</span>
            </div>
            <div class="relative flex items-center justify-center">
              <div
                class="h-3 w-3 rounded-full transition-all duration-500 relative z-10"
                :class="isDb54Connected ? 'bg-green-500' : 'bg-red-500'"
              ></div>
              <div
                v-if="isDb54Connected"
                class="absolute h-5 w-5 rounded-full bg-green-500/10 animate-ping"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-[1700px] p-6 lg:p-10 pt-8">
      <!-- Alerts Area -->
      <div class="mb-8 space-y-4">
        <Alert
          v-if="db26Error || ledError"
          variant="destructive"
          class="glass-card border-red-500/10 bg-red-50/80 text-red-600"
        >
          <WifiOff class="h-4 w-4" />
          <AlertDescription class="font-bold ml-2"
            >ERROR: {{ db26Error || ledError }}</AlertDescription
          >
        </Alert>
        <Alert
          v-if="db26Success || ledSuccess"
          class="glass-card border-green-500/10 bg-green-50/80 text-green-600"
        >
          <Wifi class="h-4 w-4" />
          <AlertDescription class="font-bold ml-2"
            >SUCCESS: {{ db26Success || ledSuccess }}</AlertDescription
          >
        </Alert>
      </div>

      <!-- Unified Grid Layout -->
      <div class="grid grid-cols-1 gap-10 lg:grid-cols-12 items-start">
        <!-- Left Column: Controls (Span 4) -->
        <div class="lg:col-span-4 space-y-6">
          <div class="flex items-center gap-4 px-2">
            <div
              class="h-8 w-1 bg-primary rounded-full shadow-[0_0_10px_rgba(14,165,233,0.5)]"
            ></div>
            <h2
              class="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground flex items-center gap-2"
            >
              System Inputs
              <Info class="h-3 w-3 opacity-50" />
            </h2>
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
            class="glass-card tech-border"
          />
        </div>

        <!-- Right Column: Monitoring (Span 8) -->
        <div class="lg:col-span-8 space-y-6">
          <div class="flex items-center gap-4 px-2">
            <div
              class="h-8 w-1 bg-secondary rounded-full shadow-[0_0_10px_rgba(168,85,247,0.5)]"
            ></div>
            <h2
              class="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground flex items-center gap-2"
            >
              Global Monitoring
              <Activity class="h-3 w-3 opacity-50" />
            </h2>
          </div>

          <LedScoreBoard :independent="false" />
        </div>
      </div>
    </main>
  </div>
</template>
