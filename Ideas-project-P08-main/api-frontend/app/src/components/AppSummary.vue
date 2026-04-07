<script setup>
defineProps({
  title: String,
})
</script>

<template>
  <h3>{{ title }}</h3>
  <slot/>
</template>
