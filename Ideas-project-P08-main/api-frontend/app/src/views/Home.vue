<script setup>
import Card from '../components/Card.vue';
import Label from '../components/Label.vue';
import Button from '../components/Button.vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useSummaryStore } from '../stores/summary.js';
import { useProcessStore } from '../stores/process.js';
import { ref } from 'vue';

const router = useRouter();
const summaryStore = useSummaryStore();
const processStore = useProcessStore();

const form = ref({
  url: '',
});

const startAcquisition = async (url) => {
  await processStore.startAcquisition(url);
};

const generateSummary = async () => {
  try {
    const response = await axios.post(import.meta.env.VITE_API_URL + '/summary');
    if (response.status === 200) {
      console.log('Summary finished:', response.data);
      summaryStore.setSummary(response.data.summary);
      processStore.setStatus('summary', 'finished');
      processStore.stopPolling();
    }
  } catch (error) {
    console.error('Summary error:', error)
    // Jak sie rozwali to i tak finished lol
    processStore.setStatus('summary', 'finished');
    processStore.stopPolling();
  }
};
</script>

<template>
  <div class="flex flex-row items-center justify-between p-5 gap-4 mb-10">
    <Card :status="processStore.statuses.acquisition">Acquisition</Card>
    <Card :status="processStore.statuses.differentiation">Differentiation</Card>
    <Card :status="processStore.statuses.summary">Summary</Card>
  </div>
  <Label class="text-base">{{ processStore.currentUrl }}</Label>

  <form @submit.prevent="startAcquisition(form.url)" method="post" class="flex flex-col w-3/4 p-5 gap-2">
    <input v-model="form.url" class="bg-white text-black border-2 border-gray-300 rounded-lg p-2 w-full mb-4" type="text" placeholder="Enter URL to start process" />
    <Button type="submit" class="bg-pink-400 text-black hover:bg-pink-300">Start process</Button>
    <Button @click="generateSummary" class="bg-pink-400 mt-2 text-black hover:bg-pink-300">Generate summary</Button>
  </form>
</template>
