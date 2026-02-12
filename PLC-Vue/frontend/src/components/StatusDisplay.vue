<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import type { MarkerState } from '../composables/usePlcClient';

defineProps<{
  markerData: MarkerState;
  plcConnected: boolean;
}>();

const emit = defineEmits<{
  (e: 'updateLineUse', bit: number, value: boolean): void;
}>();

const handleLineUseChange = (bit: number, checked: boolean) => {
  emit('updateLineUse', bit, checked);
};
</script>

<template>
  <Card>
    <CardHeader class="pb-3">
      <CardTitle>PLC Status</CardTitle>
    </CardHeader>
    <CardContent class="space-y-6">
      <!-- Status Indicator -->
      <div class="flex items-center justify-between bg-muted/40 p-2 rounded-lg border">
        <span class="text-sm font-medium text-muted-foreground">SENT DATA (%M150.0)</span>
        <div class="flex items-center gap-2">
          <div :class="['w-2 h-2 rounded-full animate-pulse', markerData.sentData ? 'bg-green-500' : 'bg-red-500']"></div>
          <span :class="['text-sm font-bold', markerData.sentData ? 'text-green-600' : 'text-muted-foreground']">
            {{ markerData.sentData ? 'ON' : 'OFF' }}
          </span>
        </div>
      </div>
      
      <!-- Line Controls Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Line 1 -->
        <div class="flex items-center justify-between space-x-4 border p-3 rounded-lg hover:bg-muted/40 transition-colors">
          <div class="flex flex-col space-y-1">
            <Label for="line1" class="text-sm font-bold">บรรทัดที่ 1</Label>
            <span class="text-xs text-muted-foreground">LINE 1 USE</span>
          </div>
          <Switch
            id="line1"
            :checked="markerData.line1Use"
            @update:checked="(val) => handleLineUseChange(0, val)"
            :disabled="!plcConnected"
          />
        </div>
        
        <!-- Line 2 -->
        <div class="flex items-center justify-between space-x-4 border p-3 rounded-lg hover:bg-muted/40 transition-colors">
          <div class="flex flex-col space-y-1">
            <Label for="line2" class="text-sm font-bold">บรรทัดที่ 2</Label>
            <span class="text-xs text-muted-foreground">LINE 2 USE</span>
          </div>
          <Switch
            id="line2"
            :checked="markerData.line2Use"
            @update:checked="(val) => handleLineUseChange(1, val)"
            :disabled="!plcConnected"
          />
        </div>
        
        <!-- Line 3 -->
        <div class="flex items-center justify-between space-x-4 border p-3 rounded-lg hover:bg-muted/40 transition-colors">
          <div class="flex flex-col space-y-1">
            <Label for="line3" class="text-sm font-bold">บรรทัดที่ 3</Label>
            <span class="text-xs text-muted-foreground">LINE 3 USE</span>
          </div>
          <Switch
            id="line3"
            :checked="markerData.line3Use"
            @update:checked="(val) => handleLineUseChange(2, val)"
            :disabled="!plcConnected"
          />
        </div>
        
        <!-- Line 4 -->
        <div class="flex items-center justify-between space-x-4 border p-3 rounded-lg hover:bg-muted/40 transition-colors">
          <div class="flex flex-col space-y-1">
            <Label for="line4" class="text-sm font-bold">บรรทัดที่ 4</Label>
            <span class="text-xs text-muted-foreground">LINE 4 USE</span>
          </div>
          <Switch
            id="line4"
            :checked="markerData.line4Use"
            @update:checked="(val) => handleLineUseChange(3, val)"
            :disabled="!plcConnected"
          />
        </div>
      </div>
    </CardContent>
  </Card>
</template>
