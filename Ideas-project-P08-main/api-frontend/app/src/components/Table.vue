<script setup>
import Button from './Button.vue';

defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  headers: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['summary']);
</script>

<template>
  <section class="container px-4 mx-auto">
    <div class="flex items-center gap-x-3">
      <h2 class="text-lg font-medium text-gray-800 dark:text-gray-800">Number of Summaries</h2>

      <span
          class="px-3 py-1 text-xs font-bold text-pink-600 bg-indigo-100 rounded-full dark:bg-cyan-200 dark:text-pink-600">{{
          items.length
        }}</span>
    </div>

    <div class="flex flex-col mt-6">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div class="overflow-hidden border border-indigo-600 dark:border-gray-300 md:rounded-lg">
            <table class="w-full table-auto divide-y divide-indigo-200 dark:divide-gray-300">
              <thead class="bg-indigo-100 dark:bg-gray-200">
              <tr>
                <th v-for="header in headers" :key="header.id"
                    scope="col"
                    class="px-4 py-3.5 text-sm font-normal text-center rtl:text-right text-indigo-900 hover:text-pink-600 dark:text-gray-800 ">
                  {{ header.name }}
                </th>
              </tr>
              </thead>
              <tbody class="bg-white divide-y divide-indigo-200 dark:divide-gray-300 dark:bg-gray-200">

              <tr v-for="item in items" :key="item.id">
                <td class="px-4 py-4 text-sm text-left font-medium text-indigo-700 max-w-xs break-words whitespace-normal ">
                      <h2 class="font-medium text-indigo-800 dark:text-gray-800">{{ item.url }}</h2>
                </td>

                <td class="px-4 py-4 text-sm text-center text-gray-800 hover:text-gray-800 dark:text-gray-800 whitespace-nowrap">
                  {{ item.generatedAt }}
                </td>

                <td class="px-4 py-4 text-sm text-center text-gray-500 hover:text-gray-800 dark:text-gray-800 whitespace-nowrap">
                  <Button
                      class="px-4 py-2 bg-pink-200 !text-gray-700 hover:bg-pink-300 border-5 border-pink-300"
                      size="sm"
                      @click="emit('summary', item)"
                  >Get summary</Button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>