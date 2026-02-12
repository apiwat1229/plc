<script setup lang="ts">
import { Card } from "@/components/ui/card";
import {
  COLOR_OPTIONS,
  TEXT_OPTIONS,
  type PoolData,
} from "@/composables/useDb54";
import { ChevronDown, Palette, Type } from "lucide-vue-next";
import { computed, ref, watch } from "vue";

const props = defineProps<{
  poolNumber: number;
  pool: PoolData;
  brightness: number;
  hasData: boolean;
}>();

const emit = defineEmits<{
  (e: "update:color", color: number): void;
  (e: "update:text", text: number): void;
}>();

const isPickingColor = ref(false);
const isPickingText = ref(false);

const localColor = ref(props.pool.color);
const localText = ref(props.pool.text);

watch(
  () => props.pool.color,
  (newVal) => {
    localColor.value = newVal;
  },
);
watch(
  () => props.pool.text,
  (newVal) => {
    localText.value = newVal;
  },
);

const colorOption = computed(() => {
  return (
    COLOR_OPTIONS.find((opt) => opt.value === localColor.value) ||
    COLOR_OPTIONS[0]
  );
});

const colorClass = computed(() => colorOption.value?.color || "bg-red-500");

const textLabel = computed(() => {
  const option = TEXT_OPTIONS.find((opt) => opt.value === localText.value);
  return option ? option.label : "REG";
});

const handleColorChange = (color: number) => {
  localColor.value = color;
  emit("update:color", color);
  isPickingColor.value = false;
};

const handleTextChange = (text: number) => {
  localText.value = text;
  emit("update:text", text);
  isPickingText.value = false;
};

const toggleTextPicker = () => {
  isPickingText.value = !isPickingText.value;
  isPickingColor.value = false;
};

const toggleColorPicker = () => {
  isPickingColor.value = !isPickingColor.value;
  isPickingText.value = false;
};
</script>

<template>
  <Card
    class="group relative glass-card tech-border p-0 aspect-[1/0.7] flex flex-col items-center justify-center overflow-visible transition-all duration-300 hover:scale-[1.03] hover:bg-white/60"
    :class="{
      'z-[110] border-primary/50': isPickingColor || isPickingText,
    }"
  >
    <!-- Overlay -->
    <div
      v-if="isPickingColor || isPickingText"
      @click.stop="
        isPickingColor = false;
        isPickingText = false;
      "
      class="fixed inset-0 z-40 bg-slate-900/20 cursor-default"
    ></div>

    <!-- P Number (Top Left Badge) -->
    <div
      class="absolute top-2 left-2 px-1.5 py-0.5 rounded-md bg-slate-100 border border-black/10 text-[9px] font-black text-muted-foreground/50 tracking-widest z-10 transition-colors group-hover:text-primary/70"
    >
      P{{ poolNumber.toString().padStart(2, "0") }}
    </div>

    <!-- Quick Actions (Top Right) -->
    <div
      class="absolute top-2 right-2 flex gap-1 z-10 opacity-0 group-hover:opacity-100 transition-opacity"
    >
      <button
        @click.stop="toggleTextPicker"
        class="p-1.5 rounded-lg bg-slate-100 border border-black/5 hover:bg-primary/10 text-muted-foreground/50 hover:text-primary transition-all"
      >
        <Type class="h-3 w-3" />
      </button>
      <button
        @click.stop="toggleColorPicker"
        class="p-1.5 rounded-lg bg-slate-100 border border-black/5 hover:bg-primary/10 text-muted-foreground/50 hover:text-primary transition-all"
      >
        <Palette class="h-3 w-3" />
      </button>
    </div>

    <!-- Popovers -->
    <div
      v-if="isPickingText"
      @click.stop
      class="absolute inset-2 glass-card border-black/10 rounded-2xl z-[120] flex items-center justify-center p-2 shadow-sm animate-in fade-in zoom-in duration-200"
    >
      <div class="flex flex-col gap-1.5 w-full max-w-[100px]">
        <button
          v-for="option in TEXT_OPTIONS"
          :key="option.value"
          @click="handleTextChange(option.value)"
          class="w-full py-2 flex items-center justify-center rounded-xl border border-black/5 hover:bg-primary/10 transition-all group/opt"
          :class="{
            'bg-primary/5 border-primary/20': localText === option.value,
          }"
        >
          <span
            class="text-[10px] font-black uppercase tracking-[0.1em] text-muted-foreground group-hover/opt:text-primary"
            :class="{ 'text-primary': localText === option.value }"
          >
            {{ option.label }}
          </span>
        </button>
      </div>
    </div>

    <div
      v-if="isPickingColor"
      @click.stop
      class="absolute inset-2 glass-card border-black/10 rounded-2xl z-[120] flex items-center justify-center p-2 shadow-sm animate-in fade-in zoom-in duration-200"
    >
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="option in COLOR_OPTIONS"
          :key="option.value"
          @click="handleColorChange(option.value)"
          class="w-8 h-8 rounded-lg border border-black/10 hover:scale-110 active:scale-95 transition-all shrink-0 relative overflow-hidden"
          :class="[
            option.color,
            {
              'ring-2 ring-primary ring-offset-2 ring-offset-white':
                localColor === option.value,
            },
          ]"
        >
          <div
            class="absolute inset-0 bg-gradient-to-tr from-black/5 to-transparent"
          ></div>
        </button>
      </div>
    </div>

    <!-- Main Content Display -->
    <div
      @click="toggleColorPicker"
      class="flex flex-col items-center cursor-pointer select-none"
    >
      <!-- Large Symbolic Status (Clean - No Shadow) -->
      <div
        class="text-[42px] font-black tracking-tighter leading-none mb-1 transition-transform group-hover:scale-110"
        :class="[
          localColor === 0
            ? 'text-red-700'
            : localColor === 1
              ? 'text-amber-600'
              : localColor === 2
                ? 'text-emerald-700'
                : localColor === 3
                  ? 'text-sky-700'
                  : localColor === 4
                    ? 'text-blue-800'
                    : localColor === 5
                      ? 'text-pink-700'
                      : 'text-primary',
        ]"
      >
        <span class="inline-block" :class="{ 'opacity-50': localColor === 0 }">
          {{
            localColor === 0
              ? "X"
              : localColor === 1
                ? "—"
                : localColor === 2
                  ? "↑"
                  : "↓"
          }}
        </span>
      </div>

      <!-- Secondary Label -->
      <div
        class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 border border-black/10 group-hover:border-primary/40 transition-all"
      >
        <span
          class="text-[12px] font-black uppercase tracking-widest text-foreground/80"
          >{{ textLabel }}</span
        >
        <ChevronDown
          class="h-3 w-3 text-muted-foreground/30 group-hover:text-primary transition-colors"
        />
      </div>
    </div>

    <!-- Pulse Effect for Active Status -->
    <div
      v-if="localColor !== 0"
      class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-8 h-1 bg-gradient-to-r from-transparent via-primary/40 to-transparent blur-sm rounded-full"
    ></div>
  </Card>
</template>

<style scoped>
.text-4xl {
  transition: color 0.15s ease-out;
}
</style>
