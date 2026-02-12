<template>
  <div class="space-y-6">
    <!-- Compact Monitoring Header -->
    <!-- Compact Monitoring Header -->
    <div
      class="glass-card p-3 px-5 rounded-2xl border-black/10 tech-border overflow-hidden"
    >
      <div class="flex flex-wrap items-center gap-6">
        <!-- Group 2: Brightness Control (Slimmer) -->
        <div
          class="flex-1 min-w-[200px] bg-slate-100/50 p-2 px-4 rounded-xl border border-black/10"
        >
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2 shrink-0">
              <Sun class="h-3 w-3 text-primary" />
              <span
                class="text-[9px] uppercase font-bold tracking-wider text-muted-foreground whitespace-nowrap"
                >Brightness</span
              >
            </div>
            <Slider
              :model-value="[brightness]"
              @update:model-value="
                (val) => val?.[0] !== undefined && updateBrightness(val[0])
              "
              :max="4"
              :step="1"
              class="flex-1 h-4"
            />
            <span
              class="text-[10px] font-black text-primary min-w-[30px] text-right"
            >
              {{ BRIGHTNESS_OPTIONS[brightness]?.label || "0%" }}
            </span>
          </div>
        </div>

        <!-- Group 3: Global Actions (Slimmer) -->
        <div class="flex items-center gap-3">
          <button
            @click="writeAndPulse"
            :disabled="!isConnected || isLoading"
            class="h-9 px-6 rounded-xl font-black text-[10px] uppercase tracking-wider bg-primary hover:bg-primary/90 text-primary-foreground border border-black/10 transition-all active:scale-95 flex items-center gap-2"
          >
            <RefreshCcw v-if="isLoading" class="h-3 w-3 animate-spin" />
            <Activity v-else class="h-3 w-3" />
            <span>{{ isLoading ? "Syncing..." : "Update" }}</span>
          </button>
          <Button
            @click="handleReset"
            :disabled="!isConnected || isLoading"
            variant="ghost"
            size="sm"
            class="h-9 px-3 rounded-xl text-[9px] font-bold uppercase tracking-wider text-muted-foreground hover:bg-red-50 hover:text-red-600 border border-transparent hover:border-red-200"
          >
            <RotateCcw class="h-3 w-3 mr-1" />
            Reset
          </Button>
        </div>
      </div>
    </div>

    <!-- Alerts (Bottom Toast) -->
    <div
      v-if="error || successMessage"
      class="fixed bottom-6 right-6 z-[100] w-80 animate-in slide-in-from-right duration-500"
    >
      <Alert
        v-if="error"
        variant="destructive"
        class="glass-card border-red-500/20 bg-red-50/90 text-red-600 backdrop-blur-2xl"
      >
        <WifiOff class="h-4 w-4" />
        <AlertDescription class="text-xs font-bold leading-tight">{{
          error
        }}</AlertDescription>
      </Alert>
      <Alert
        v-if="successMessage"
        class="glass-card border-green-500/20 bg-green-50/90 text-green-600 backdrop-blur-2xl"
      >
        <Wifi class="h-4 w-4" />
        <AlertDescription class="text-xs font-bold leading-tight">{{
          successMessage
        }}</AlertDescription>
      </Alert>
    </div>

    <!-- Pools Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <PoolCard
        v-for="(pool, index) in pools"
        :key="index"
        :pool-number="index + 1"
        :pool="pool"
        :brightness="brightness"
        :has-data="hasData"
        @update:color="(color) => updatePoolColor(index, color)"
        @update:text="(text) => updatePoolText(index, text)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { useDb54 } from "@/composables/useDb54";
import {
  Activity,
  RefreshCcw,
  RotateCcw,
  Sun,
  Wifi,
  WifiOff,
} from "lucide-vue-next";
import { ref, watch } from "vue";
import PoolCard from "./PoolCard.vue";

const props = defineProps<{
  independent?: boolean;
}>();

const ledIpAddress = ref("192.168.190.53");

const {
  isConnected,
  brightness,
  pools,
  error,
  successMessage,
  isLoading,
  hasData,
  isSocketConnected,
  connectToPlc,
  writeAndPulse,
  updatePoolColor,
  updatePoolText,
  updateBrightness,
  resetAll,
  BRIGHTNESS_OPTIONS,
} = useDb54();

watch(
  isSocketConnected,
  (connected) => {
    if (connected && !isConnected.value && props.independent) {
      handleConnect();
    }
  },
  { immediate: true },
);

const handleConnect = () => {
  if (props.independent) {
    connectToPlc(ledIpAddress.value);
  }
};

const handleReset = () => {
  if (confirm("คุณต้องการรีเซ็ตค่าทั้งหมดหรือไม่?")) {
    resetAll();
  }
};
</script>
