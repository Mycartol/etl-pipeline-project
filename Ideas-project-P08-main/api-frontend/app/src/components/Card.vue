<script setup>
import Label from "./Label.vue";

defineProps({
  status: {
    type: String,
    default: 'not_started', // 'not_started', 'in_progress', 'finished'
  },
})

const statusText = {
  not_started: 'Not started',
  in_progress: 'In progress',
  finished: 'Finished',
}
</script>

<template>
<div class="flex flex-col items-center justify-between min-w-100 min-h-100 rounded-lg p-4 bg-gray-100 shadow-lg">
  <span class="font-bold text-3xl text-gray-800"><slot/></span>
  <p class="font-bold text-4xl text-gray-800">{{ statusText[status] }}</p>
  <Label class="bg-pink-300">Status</Label>
</div>
</template>
