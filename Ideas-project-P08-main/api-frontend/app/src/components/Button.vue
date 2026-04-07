<script setup>
import { computed } from "vue";

const props = defineProps({
  class: {
    type: String,
    required: false,
    default: 'bg-gray-500 text-white hover:bg-gray-600'
  },
  type: {
    type: String,
    default: 'button'
  },
  size: {
    type: String,
    default: 'md'
  }
})

const emit = defineEmits(['click'])

const baseClasses = 'font-bold !rounded-xl hover:bg-pink-300 transition duration-300 ease-in-out'

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm': return '!text-sm !py-2 !px-4';
    case 'lg': return '!text-xl !py-5 !px-10';
    default: return '!text-2xl !py-6 !px-16';
  }
});

const classes = computed(() => {
  return [
    baseClasses,
    props.class,
    sizeClasses.value
  ].join(' ');
});
</script>

<template>
  <button
      :class="classes"
      @click="emit('click')"
      :type="props.type"
  >
    <slot/>
  </button>
</template>
