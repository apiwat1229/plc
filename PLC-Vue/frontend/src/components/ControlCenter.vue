<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { RefreshCcw, Terminal, Zap } from "lucide-vue-next";
import { ref, watch } from "vue";
import type { MarkerState } from "../composables/usePlcClient";

const props = defineProps<{
  markerData: MarkerState;
  dbData: number[];
  plcConnected: boolean;
  hasData: boolean;
  isProcessing?: boolean;
  independent?: boolean;
}>();

const emit = defineEmits<{
  (e: "updateLineUse", bit: number, value: boolean): void;
  (e: "connect", ip: string): void;
  (e: "disconnect"): void;
  (e: "writeAndPulse"): void;
  (e: "reload"): void;
}>();

const LINE_CONFIG = [1, 2, 3, 4];
const ipAddress = ref("192.168.190.51");

const handleConnect = () => {
  emit("connect", ipAddress.value);
};

const handleDisconnect = () => {
  emit("disconnect");
};

const handleWriteAndPulse = () => {
  emit("writeAndPulse");
};

const handleReload = () => {
  emit("reload");
};

const handleLineUseChange = (lineIndex: number, checked: boolean) => {
  emit("updateLineUse", lineIndex, checked);
};

const getLineStatus = (index: number): boolean => {
  const key = `line${index + 1}Use` as keyof MarkerState;
  return !!props.markerData[key];
};

const localValues = ref<string[]>([]);

watch(
  [() => props.dbData, () => props.hasData],
  ([newData, newHasData]) => {
    if (!newHasData) {
      localValues.value = Array(8).fill("");
    } else {
      localValues.value = newData.map((v) => String(v));
    }
  },
  { immediate: true },
);

const getValues = (): number[] => {
  return localValues.value.map((v) => parseInt(v) || 0);
};

defineExpose({ getValues });
</script>

<template>
  <Card class="border-none bg-transparent shadow-none">
    <div class="p-6 pb-4 flex flex-col gap-6">
      <!-- Actions Row -->
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <Button
            @click="handleWriteAndPulse"
            :disabled="!plcConnected || isProcessing"
            size="sm"
            class="h-10 px-8 text-xs font-black uppercase tracking-[0.15em] bg-primary hover:bg-primary/90 text-primary-foreground border border-black/5 rounded-xl transition-all active:scale-95 group"
          >
            <Zap class="h-4 w-4 mr-2 group-hover:animate-pulse" />
            Update Sync
          </Button>
          <Button
            @click="handleReload"
            :disabled="!plcConnected || isProcessing"
            variant="ghost"
            size="sm"
            class="h-10 px-5 text-[10px] font-black uppercase tracking-widest text-primary hover:bg-primary/5 border border-transparent hover:border-primary/20 rounded-xl transition-all"
          >
            <RefreshCcw
              class="h-3 w-3 mr-2"
              :class="{ 'animate-spin': isProcessing }"
            />
            Read Data
          </Button>
        </div>

        <div v-if="independent" class="flex items-center gap-3">
          <div class="relative group">
            <Terminal
              class="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground group-focus-within:text-primary transition-colors"
            />
            <Input
              v-model="ipAddress"
              placeholder="0.0.0.0"
              class="h-9 w-[160px] pl-9 font-mono text-[10px] bg-slate-50 border-black/10 text-foreground rounded-xl focus:ring-primary/20"
              :disabled="plcConnected"
            />
          </div>
          <Button
            @click="plcConnected ? handleDisconnect() : handleConnect()"
            :variant="plcConnected ? 'destructive' : 'default'"
            size="sm"
            class="h-9 rounded-xl text-[10px] font-black uppercase px-6"
          >
            {{ plcConnected ? "OFFLINE" : "ONLINE" }}
          </Button>
        </div>
      </div>

      <!-- Line Controls Grid -->
      <div class="grid grid-cols-1 gap-4">
        <div
          v-for="(_, index) in LINE_CONFIG"
          :key="index"
          class="group relative glass-card p-5 rounded-3xl border-black/10 transition-all hover:bg-white/60 hover:border-primary/40 overflow-hidden flex flex-col gap-4"
        >
          <!-- Background Glow Effect (Softer - Pulse Only) -->
          <div
            class="absolute left-0 top-0 w-1 h-full bg-primary/40 opacity-0 group-hover:opacity-100 transition-opacity"
          ></div>

          <!-- Status & Toggle -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                class="h-8 w-8 rounded-xl bg-slate-100 flex items-center justify-center font-bold text-xs text-primary border border-black/10"
              >
                0{{ index + 1 }}
              </div>
              <span
                class="text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em] group-hover:text-foreground transition-colors"
              >
                Production Line
              </span>
            </div>
            <div
              class="flex items-center gap-3 bg-slate-100/80 p-1 padding-left-3 rounded-full border border-black/10"
            >
              <span
                class="text-[8px] font-black uppercase tracking-widest text-muted-foreground ml-2"
              >
                {{ getLineStatus(index) ? "ACTIVE" : "IDLE" }}
              </span>
              <Switch
                :id="`line-${index}`"
                :checked="getLineStatus(index)"
                @update:checked="(val) => handleLineUseChange(index, val)"
                :disabled="!plcConnected"
                class="data-[state=checked]:bg-primary"
              />
            </div>
          </div>

          <!-- Inputs Grid -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label
                class="text-[10px] text-muted-foreground font-black uppercase tracking-widest flex items-center gap-1.5 ml-1"
              >
                <div class="h-1 w-1 rounded-full bg-primary/50"></div>
                Pool No.
              </Label>
              <div class="relative">
                <Input
                  v-model="localValues[index * 2]"
                  type="number"
                  :disabled="!plcConnected"
                  class="h-11 px-4 text-sm font-mono font-bold bg-slate-50 border-black/10 text-foreground rounded-xl focus:ring-1 focus:ring-primary/40 transition-all text-center"
                  placeholder="00"
                />
              </div>
            </div>
            <div class="space-y-2">
              <Label
                class="text-[10px] text-muted-foreground font-black uppercase tracking-widest flex items-center gap-1.5 ml-1"
              >
                <div class="h-1 w-1 rounded-full bg-secondary/50"></div>
                Scoops
              </Label>
              <div class="relative">
                <Input
                  v-model="localValues[index * 2 + 1]"
                  type="number"
                  :disabled="!plcConnected"
                  class="h-11 px-4 text-sm font-mono font-bold bg-slate-50 border-black/10 text-foreground rounded-xl focus:ring-1 focus:ring-secondary/40 transition-all text-center"
                  placeholder="000"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>
