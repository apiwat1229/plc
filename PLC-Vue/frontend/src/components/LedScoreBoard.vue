<template>
<div class="space-y-4 p-4 max-w-[1400px] mx-auto">
    <!-- Compact Monitoring Header -->
    <Card class="bg-white shadow-sm border-slate-200 overflow-hidden mb-4 rounded-2xl">
      <CardContent class="p-4 bg-slate-50/50">
        <div class="flex flex-wrap items-center gap-6">
          <!-- Group 2: Brightness Control -->
          <div class="flex-1 min-w-[300px] bg-white p-3 px-5 rounded-xl border border-slate-200 shadow-sm">
            <div class="flex flex-col">
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-[10px] uppercase font-black tracking-widest text-slate-400">Board Brightness</span>
                <span class="text-xs font-black text-blue-600">
                  {{ BRIGHTNESS_OPTIONS[brightness]?.label || '0%' }}
                </span>
              </div>
              <div class="flex items-center gap-4 h-6">
                <Slider
                  :model-value="[brightness]"
                  @update:model-value="(val) => val?.[0] !== undefined && updateBrightness(val[0])"
                  :max="4"
                  :step="1"
                  class="flex-1"
                />
                <span class="text-[9px] font-black text-slate-300 uppercase tracking-tighter w-8">
                  {{ brightness === 4 ? 'MAX' : 'BRT' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Group 3: Global Actions -->
          <div class="flex items-center gap-2">
            <Button
              @click="writeAndPulse"
              :disabled="!isConnected || isLoading"
              size="sm"
              class="h-10 px-6 rounded-xl font-black text-xs uppercase shadow-md shadow-blue-500/10 bg-blue-600 hover:bg-blue-700 transition-all active:scale-95 text-white"
            >
              <span v-if="isLoading" class="flex items-center gap-2">
                <div class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Wait
              </span>
              <span v-else>Update Board</span>
            </Button>
            <Button
              @click="handleReset"
              :disabled="!isConnected || isLoading"
              variant="outline"
              size="sm"
              class="h-10 px-4 rounded-xl text-[10px] font-black uppercase text-slate-400 border-slate-200 bg-white hover:bg-red-50 hover:text-red-600 hover:border-red-200"
            >
              Reset
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Alerts (Bottom Toast) -->
    <div v-if="error || successMessage" class="fixed bottom-4 right-4 z-[100] w-72 animate-in slide-in-from-right duration-300">
      <Alert v-if="error" variant="destructive" class="shadow-xl py-2 px-3 border-none bg-destructive text-destructive-foreground">
        <AlertDescription class="text-[10px] font-bold">{{ error }}</AlertDescription>
      </Alert>
      <Alert v-if="successMessage" class="bg-primary border-none text-primary-foreground shadow-xl py-2 px-3">
        <AlertDescription class="text-[10px] font-bold">{{ successMessage }}</AlertDescription>
      </Alert>
    </div>

    <!-- Pools Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-1.5">
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { useDb54 } from '@/composables/useDb54';
import { ref } from 'vue';
import PoolCard from './PoolCard.vue';

const props = defineProps<{
  independent?: boolean;
}>();

const ledIpAddress = ref('192.168.190.53');

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

import { watch } from 'vue';

watch(isSocketConnected, (connected) => {
  if (connected && !isConnected.value && props.independent) {
    handleConnect();
  }
}, { immediate: true });

const handleConnect = () => {
  if (props.independent) {
    connectToPlc(ledIpAddress.value);
  }
};

const handleReset = () => {
  if (confirm('คุณต้องการรีเซ็ตค่าทั้งหมดหรือไม่?')) {
    resetAll();
  }
};
</script>
