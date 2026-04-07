<script setup>
import Label from '../components/Label.vue';
import Table from '../components/Table.vue';
import { computed, onMounted, ref } from 'vue';
import { useSummaryStore } from '../stores/summary.js';
import axios from 'axios';

const headers = [
  { id: 1, name: 'URL' },
  { id: 2, name: 'Generated at' },
  { id: 3, name: 'Summary' }
];

const items = ref([]);
const summaryStore = useSummaryStore();
const filterUrl = ref('');

onMounted(async () => {
  const { data } = await axios.get(`${import.meta.env.VITE_API_URL}/diffs/all`);
  items.value = data.map(item => ({
    id: item._id,
    url: item.url,
    generatedAt: new Date(item.generated_at).toLocaleString(),
  }));
});

const getSummary = async (item) => {
  const { data } = await axios.get(`${import.meta.env.VITE_API_URL}/diffs/${item.id}/description`);
  summaryStore.setSummary(data.description);
};

const filteredItems = computed(() => {
  if (!filterUrl.value) return items.value;
  return items.value.filter(item =>
    item.url.toLowerCase().includes(filterUrl.value.toLowerCase())
  );
});


</script>

<template>
  <Label class="mb-5 bg-pink-400">Finished processes</Label>
  <input v-model="filterUrl" class="bg-white text-black border-2 border-gray-300 rounded-lg p-2 w-full mb-4" type="text" placeholder="Filter URLs" />
  <Table :headers="headers" :items="filteredItems" @summary="getSummary"/>
</template>
