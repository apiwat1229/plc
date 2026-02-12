<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ref, watch } from 'vue';

const props = defineProps<{
  dbData: number[];
  plcConnected: boolean;
  hasData: boolean;
}>();

const DB_TAGS = [
  { label: 'Data_Center[1]', desc: 'หมายเลขบ่อ บรรทัดที่ 1' },
  { label: 'Data_Center[3]', desc: 'จำนวนตัก บรรทัดที่ 1' },
  { label: 'Data_Center[5]', desc: 'หมายเลขบ่อ บรรทัดที่ 2' },
  { label: 'Data_Center[7]', desc: 'จำนวนตัก บรรทัดที่ 2' },
  { label: 'Data_Center[9]', desc: 'หมายเลขบ่อ บรรทัดที่ 3' },
  { label: 'Data_Center[11]', desc: 'จำนวนตัก บรรทัดที่ 3' },
  { label: 'Data_Center[13]', desc: 'หมายเลขบ่อ บรรทัดที่ 4' },
  { label: 'Data_Center[15]', desc: 'จำนวนตัก บรรทัดที่ 4' },
];

const localValues = ref<string[]>([]);

watch(
  [() => props.dbData, () => props.hasData],
  ([newData, newHasData]) => {
    if (!newHasData) {
      localValues.value = Array(DB_TAGS.length).fill('');
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
  <Card class="col-span-2">
    <CardHeader>
      <CardTitle>Data Center (DB26)</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[180px]">Tag</TableHead>
              <TableHead>Description</TableHead>
              <TableHead class="w-[200px]">Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="(tag, index) in DB_TAGS" :key="index">
              <TableCell class="font-mono text-primary">{{ tag.label }}</TableCell>
              <TableCell class="text-muted-foreground">{{ tag.desc }}</TableCell>
              <TableCell>
                <Input
                  v-model="localValues[index]"
                  type="number"
                  :disabled="!plcConnected"
                  class="font-mono"
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </CardContent>
  </Card>
</template>
