import { defineStore } from 'pinia';

export const useSummaryStore = defineStore('summary', {
  state: () => ({
    text: ''
  }),
  actions: {
    setSummary(newText) {
      this.text = newText;
    }
  }
});