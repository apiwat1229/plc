<script setup lang="ts">
import { cn } from '@/lib/utils';
import { SwitchRoot, SwitchThumb } from 'radix-vue';

const props = defineProps<{
  checked?: boolean
  disabled?: boolean
  id?: string
}>()

const emits = defineEmits<{
  (e: 'update:checked', payload: boolean): void
}>()

const handleCheckedChange = (val: boolean) => {
  console.log('Switch toggled:', props.id, val);
  emits('update:checked', val);
};
</script>

<template>
  <SwitchRoot
    :checked="props.checked"
    @update:checked="handleCheckedChange"
    :disabled="props.disabled"
    :id="props.id"
    :class="cn('peer inline-flex h-[24px] w-[44px] shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input', $attrs.class ?? '')"
  >
    <SwitchThumb
      :class="cn('pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0')"
    />
  </SwitchRoot>
</template>
