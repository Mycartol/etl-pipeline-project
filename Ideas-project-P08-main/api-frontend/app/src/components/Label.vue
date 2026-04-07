<script setup>
import { computed } from 'vue';

const props = defineProps({
  class: {
    type: String,
    required: false,
    default: 'bg-cyan-300'
  },
});

const baseClasses = 'bg-cyan-300 flex items-center justify-center text-3xl text-gray-800 font-bold py-10 px-10 min-w-full  rounded-xl'

const classes = computed(() => {
  return [
    baseClasses,
    props.class,
  ].join(' ');
});
</script>

<template>
  <div
    :class="classes"
  >
    <slot />
  </div>
</template>