<script setup>
import Button from '../components/Button.vue';
import { computed } from 'vue';
import { useSummaryStore } from '../stores/summary.js';
import { useRouter } from 'vue-router';

const store = useSummaryStore();
const router = useRouter();

const summary = computed(() => {
  return store.text || 'No summary available yet.';
});
</script>

<template>
  <div
      class="flex flex-col mb-10 min-h-170 w-3/4 bg-gray-100 p-10 gap-10 rounded-lg shadow-lg"
  >
    <h1 class="text-black font-bold p-5">Summary</h1>
    <p class="text-black whitespace-pre-wrap">{{ summary }}</p>
  </div>
  <Button @click="router.back()" class="bg-pink-400 text-black">Exit</Button>
</template>