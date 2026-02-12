<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { ref, watch } from 'vue';
import type { MarkerState } from '../composables/usePlcClient';

const props = defineProps<{
  markerData: MarkerState;
  dbData: number[];
  plcConnected: boolean;
  hasData: boolean;
  isProcessing?: boolean;
  independent?: boolean;
}>();

const emit = defineEmits<{
  (e: 'updateLineUse', bit: number, value: boolean): void;
  (e: 'connect', ip: string): void;
  (e: 'disconnect'): void;
  (e: 'writeAndPulse'): void;
  (e: 'reload'): void;
}>();

const LINE_CONFIG = [1, 2, 3, 4];
const ipAddress = ref('192.168.190.51');

// --- Connection Logic ---
const handleConnect = () => {
  emit('connect', ipAddress.value);
};

const handleDisconnect = () => {
  emit('disconnect');
};

// --- Action Logic ---
const handleWriteAndPulse = () => {
  emit('writeAndPulse');
};

const handleReload = () => {
  emit('reload');
};

// Initial reload is handled by the usePlcClient on connection success
// but we keep this button explicit for the user.

// Auto reload is removed per user request. 
// Data is reloaded once on connection (handled in usePlcClient).

// --- Status Display Logic ---
const handleLineUseChange = (lineIndex: number, checked: boolean) => {
  emit('updateLineUse', lineIndex, checked);
};

const getLineStatus = (index: number): boolean => {
  const key = `line${index + 1}Use` as keyof MarkerState;
  return !!props.markerData[key];
};

// --- Data Center Logic ---
// We map lines 1-4 to pairs of inputs (Pool No, Scoops)
// Line 1: index 0 (Pool), 1 (Scoops)
// Line 2: index 2 (Pool), 3 (Scoops)
// etc.
const localValues = ref<string[]>([]);

watch(
  [() => props.dbData, () => props.hasData],
  ([newData, newHasData]) => {
    if (!newHasData) {
      localValues.value = Array(8).fill(''); // 4 lines * 2 inputs
    } else {
      localValues.value = newData.map((v) => String(v));
    }
  },
  { immediate: true }
);

const getValues = (): number[] => {
  return localValues.value.map((v) => parseInt(v) || 0);
};

defineExpose({ getValues });
</script>

<template>
  <Card class="col-span-1 md:col-span-2 shadow-sm border-slate-200">
    <CardHeader class="pb-4 border-b border-slate-100 bg-slate-50/50 space-y-4">
      <!-- Actions Row -->
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-2">
           <Button 
            @click="handleWriteAndPulse"
            :disabled="!plcConnected || isProcessing"
            size="sm"
            class="h-9 px-6 text-xs font-black uppercase tracking-widest bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/10 rounded-xl text-white"
          >
            Update Sync
          </Button>
          <Button 
            @click="handleReload"
            :disabled="!plcConnected || isProcessing"
            variant="outline"
            size="sm"
            class="h-9 px-4 text-[10px] font-black uppercase tracking-widest border-slate-200 hover:bg-slate-100 rounded-xl text-slate-500 bg-white"
          >
            Sync Read
          </Button>
        </div>

        <div v-if="independent" class="flex items-center gap-3">
           <Input 
            v-model="ipAddress" 
            placeholder="IP Address" 
            class="h-8 w-[140px] font-mono text-[10px] bg-white border-slate-200 text-slate-900" 
            :disabled="plcConnected"
          />
          <Button 
            @click="plcConnected ? handleDisconnect() : handleConnect()" 
            :variant="plcConnected ? 'destructive' : 'default'"
            size="sm" 
            class="h-8 text-[10px] font-black uppercase"
          >
            {{ plcConnected ? 'Off' : 'On' }}
          </Button>
        </div>
      </div>
    </CardHeader>
    <CardContent class="p-4 space-y-4 bg-white rounded-b-xl">
      <!-- Line Controls Loop -->
      <div v-for="(_, index) in LINE_CONFIG" :key="index" 
           class="relative overflow-hidden flex flex-col gap-3 p-4 border border-slate-100 rounded-2xl transition-all bg-slate-50/30 hover:bg-white hover:border-blue-400/50 hover:shadow-md group">
        
        <!-- Background Glow -->
        <div class="absolute -right-8 -top-8 w-24 h-24 bg-blue-500/5 blur-3xl rounded-full transition-opacity opacity-0 group-hover:opacity-100"></div>

        <!-- Row 1: Status & Switch -->
        <div class="flex items-center justify-between">
          <div class="flex flex-col">
            <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest group-hover:text-blue-600 transition-colors">
              Production Line {{ index + 1 }}
            </span>
          </div>
          <Switch
            :id="`line-${index}`"
            :checked="getLineStatus(index)"
            @update:checked="(val) => handleLineUseChange(index, val)"
            :disabled="!plcConnected"
            class="scale-90 data-[state=checked]:bg-blue-600 shadow-sm"
          />
        </div>

        <!-- Row 2: Inputs Grid -->
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <Label class="text-[9px] text-slate-500 font-bold uppercase tracking-tighter ml-1">บ่อ (Pool No.)</Label>
            <Input
              v-model="localValues[index * 2]"
              type="number"
              :disabled="!plcConnected"
              class="h-9 px-3 text-xs font-mono font-bold bg-white border-slate-200 text-slate-900 focus:ring-1 focus:ring-blue-500/50 rounded-xl transition-all"
              placeholder="0"
            />
          </div>
          <div class="space-y-1.5">
            <Label class="text-[9px] text-slate-500 font-bold uppercase tracking-tighter ml-1">จำนวน (Scoops)</Label>
            <Input
              v-model="localValues[index * 2 + 1]"
              type="number"
              :disabled="!plcConnected"
              class="h-9 px-3 text-xs font-mono font-bold bg-white border-slate-200 text-slate-900 focus:ring-1 focus:ring-blue-500/50 rounded-xl transition-all"
              placeholder="0"
            />
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
