<script setup lang="ts">
import { Card } from '@/components/ui/card';
import { COLOR_OPTIONS, TEXT_OPTIONS, type PoolData } from '@/composables/useDb54';
import { computed, ref, watch } from 'vue';

const props = defineProps<{
  poolNumber: number;
  pool: PoolData;
  brightness: number;
  hasData: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:color', color: number): void;
  (e: 'update:text', text: number): void;
}>();

const isPickingColor = ref(false);
const isPickingText = ref(false);

// Local state for instant feedback
const localColor = ref(props.pool.color);
const localText = ref(props.pool.text);

// Sync local state when props change
watch(() => props.pool.color, (newVal) => { 
  localColor.value = newVal; 
});
watch(() => props.pool.text, (newVal) => { 
  localText.value = newVal; 
});

const colorOption = computed(() => {
  return COLOR_OPTIONS.find(opt => opt.value === localColor.value) || COLOR_OPTIONS[0];
});

const colorClass = computed(() => colorOption.value?.color || 'bg-red-500');

const textLabel = computed(() => {
  const option = TEXT_OPTIONS.find(opt => opt.value === localText.value);
  return option ? option.label : 'REG';
});

const handleColorChange = (color: number) => {
  localColor.value = color; // Instant UI feedback
  emit('update:color', color);
  isPickingColor.value = false;
};

const handleTextChange = (text: number) => {
  localText.value = text; // Instant UI feedback
  emit('update:text', text);
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
    class="group relative hover:border-primary/50 transition-all duration-300 shadow-sm border-border/40 bg-card/60 aspect-[1/0.58] flex flex-col items-center justify-end pb-2.5 p-0"
    :class="{ 'z-[100] shadow-2xl border-primary/40 bg-card': isPickingColor || isPickingText }"
  >
    <!-- Click-away overlay -->
    <div v-if="isPickingColor || isPickingText" 
      @click.stop="isPickingColor = false; isPickingText = false" 
      class="fixed inset-0 z-40 bg-black/5 cursor-default"></div>

    <!-- Header Controls (Overlay) -->
    <div class="absolute top-1 left-2 right-2 flex items-center h-8 z-50">
      <!-- Left: P Number -->
      <span class="text-[11px] font-black text-black tabular-nums shrink-0 w-8">P{{ poolNumber }}</span>
      
      <!-- Center: Text Selection -->
      <div class="flex-1 flex justify-center">
        <div class="relative">
          <button 
            @click.stop="toggleTextPicker"
            class="text-[10px] font-black uppercase tracking-tighter text-primary hover:text-primary-foreground hover:bg-primary px-3 py-1.5 rounded-lg bg-primary/10 transition-all"
          >
            {{ textLabel }}
          </button>
          
          <!-- Text Options Popover -->
          <div v-if="isPickingText" 
            @click.stop
            class="absolute top-full left-1/2 -translate-x-1/2 mt-2 p-1 bg-white dark:bg-card border-2 border-border shadow-2xl rounded-xl flex flex-col z-[110] min-w-[90px] animate-in fade-in slide-in-from-top-1">
            <button v-for="option in TEXT_OPTIONS" :key="option.value" 
              @click="handleTextChange(option.value)"
              class="px-3 py-2.5 text-xs font-black text-left hover:bg-primary/10 rounded-lg transition-colors uppercase whitespace-nowrap"
              :class="{ 'text-primary bg-primary/5': localText === option.value }">
              {{ option.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Color Circle -->
      <div class="relative shrink-0 w-8 flex justify-end">
        <button
          @click.stop="toggleColorPicker"
          class="w-7 h-7 rounded-full border-2 border-background shadow-md hover:scale-110 active:scale-95 transition-all"
          :class="colorClass"
        ></button>
        
        <!-- Color Options Popover (All colors) -->
        <div v-if="isPickingColor" 
          @click.stop
          class="absolute top-full right-0 mt-2 p-1.5 bg-white dark:bg-card border-2 border-border shadow-2xl rounded-xl flex gap-1.5 z-[110] animate-in fade-in zoom-in slide-in-from-top-1 duration-200">
          <button v-for="option in COLOR_OPTIONS" :key="option.value" 
            @click="handleColorChange(option.value)"
            class="w-8 h-8 rounded-full border-2 border-background shadow-md hover:scale-125 active:scale-90 transition-all shrink-0"
            :class="[option.color, { 'ring-2 ring-primary ring-offset-2': localColor === option.value }]"></button>
        </div>
      </div>
    </div>
    
    <!-- Large Text Center (Moved to bottom) -->
    <div 
      class="text-[32px] font-black tracking-tighter leading-none transition-all duration-300 group-hover:scale-105"
      :class="[
        localColor === 0 ? 'text-red-500' :
        localColor === 1 ? 'text-yellow-500' :
        localColor === 2 ? 'text-green-500' :
        localColor === 3 ? 'text-sky-400' :
        localColor === 4 ? 'text-blue-700' :
        localColor === 5 ? 'text-pink-500' : 'text-primary'
      ]"
    >
      <span class="mr-1">
        <template v-if="localColor === 0">X</template>
        <template v-else-if="localColor === 1">-</template>
        <template v-else-if="localColor === 2">↑</template>
        <template v-else-if="localColor === 3 || localColor === 4">↓</template>
      </span>
      {{ textLabel }}
    </div>
  </Card>
</template>

<style scoped>
.text-4xl {
  transition: color 0.15s ease-out;
}
</style>
