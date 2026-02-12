<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const props = defineProps<{
  plcConnected: boolean;
  isProcessing?: boolean;
}>();

const emit = defineEmits<{
  writeAndPulse: [];
  reload: [];
}>();

const handleWriteAndPulse = () => {
  emit('writeAndPulse');
};

const handleReload = () => {
  emit('reload');
};
</script>

<template>
  <Card class="col-span-2">
    <CardHeader>
      <CardTitle>Actions</CardTitle>
    </CardHeader>
    <CardContent class="flex gap-3">
      <Button
        @click="handleWriteAndPulse"
        :disabled="!plcConnected || isProcessing"
        class="flex-1"
      >
        {{ isProcessing ? 'Processing...' : 'Write & Pulse' }}
      </Button>
      <Button
        @click="handleReload"
        :disabled="!plcConnected || isProcessing"
        variant="outline"
        class="flex-1"
      >
        Reload from DB
      </Button>
    </CardContent>
  </Card>
</template>
