<script setup>
const emit = defineEmits(['scrap']);
</script>

<template>
  <div class="grid place-items-center gap-1">
    <img src="../assets/vue.svg" alt="Vue logo" class="size-35 p-5"/>
    <form @submit.prevent="emit('scrap')">
      <button type="submit">Begin scraping</button>
    </form>
  </div>
</template>
