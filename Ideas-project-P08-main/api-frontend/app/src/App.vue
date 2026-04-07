<script setup>
import Sidebar from "./components/Sidebar.vue";
</script>

<template>
  <Sidebar/>
  <main class="max-w-screen ml-[300px] p-6 !bg-gradient-to-r !from-pink-300 !to-cyan-200">
    <RouterView/>
  </main>
</template>
