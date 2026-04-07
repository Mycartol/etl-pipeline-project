<script setup>
const links = [
  {name: "Home", path: "/"},
  {name: "Summary", path: "/summary"},
  {name: "Finished", path: "/finished"},

];
</script>

<template>
  <div class="fixed top-0 left-0 h-screen min-h-screen !w-[300px] !bg-gradient-to-r !from-cyan-300 !to-cyan-100 p-5 flex flex-col gap-20 items-stretch justify-center">
    <div v-for="link in links" :key="link.name">
      <RouterLink
          :to="link.path"
          class="block text-center  bg-pink-200 !text-gray-700 hover:bg-pink-300 min-w-50 border-5 border-pink-300  rounded-xl px-10 py-5"
      >
        {{ link.name }}
      </RouterLink>
    </div>
  </div>
</template>

