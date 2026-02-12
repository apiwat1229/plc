<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ref } from 'vue';

const props = defineProps<{
  isConnected: boolean;
  plcConnected: boolean;
}>();

const emit = defineEmits<{
  connect: [ip: string];
  disconnect: [];
}>();

const ipAddress = ref('192.168.190.51');

const handleConnect = () => {
  emit('connect', ipAddress.value);
};

const handleDisconnect = () => {
  emit('disconnect');
};
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>PLC Connection</CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid w-full items-center gap-1.5">
        <Label for="ip-address">IP Address</Label>
        <Input
          id="ip-address"
          v-model="ipAddress"
          type="text"
          :disabled="plcConnected"
          placeholder="192.168.190.51"
        />
      </div>
      
      <div class="flex gap-2">
        <Button
          @click="handleConnect"
          :disabled="!isConnected || plcConnected"
          class="flex-1"
        >
          Connect
        </Button>
        <Button
          @click="handleDisconnect"
          :disabled="!plcConnected"
          variant="outline"
          class="flex-1"
        >
          Disconnect
        </Button>
      </div>
      
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium">Connection:</span>
        <span :class="[
          'text-sm font-bold',
          plcConnected ? 'text-green-600' : 'text-destructive'
        ]">
          {{ plcConnected ? 'CONNECTED' : 'DISCONNECTED' }}
        </span>
      </div>
    </CardContent>
  </Card>
</template>
