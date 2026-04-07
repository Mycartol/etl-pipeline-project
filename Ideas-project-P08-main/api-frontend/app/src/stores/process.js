import { defineStore } from 'pinia';
import axios from 'axios';

export const useProcessStore = defineStore('process', {
  state: () => ({
    statuses: {
      acquisition: 'not_started',
      differentiation: 'not_started',
      summary: 'not_started',
    },
    pollingIntervalId: null,
    urlIntervalId: null,
    currentUrl: null,
  }),

  actions: {
    async checkStatus () {
      try {
        const { data } = await axios.get(import.meta.env.VITE_API_URL + '/status');
        if (data.current_stage === 'akwizycja') {
          this.statuses.acquisition = 'in_progress';
          this.statuses.differentiation = 'not_started';
          this.statuses.summary = 'not_started';
        } else if (data.current_stage === 'wersjonowanie') {

          if (this.urlIntervalId !== null) {
            clearInterval(this.urlIntervalId);
            this.urlIntervalId = null;
            this.currentUrl = 'Acquisition finished';
          }

          this.statuses.acquisition = 'finished';
          this.statuses.differentiation = 'in_progress';
          this.statuses.summary = 'not_started';
        } else if (data.current_stage === 'podsumowanie') {
          this.statuses.acquisition = 'finished';
          this.statuses.differentiation = 'finished';
          this.statuses.summary = 'in_progress';
        } else if (data.current_stage === 'finished') {
          this.statuses.acquisition = 'finished';
          this.statuses.differentiation = 'finished';
          this.statuses.summary = 'finished';

          if (this.pollingIntervalId !== null) {
            clearInterval(this.pollingIntervalId);
            this.pollingIntervalId = null;
          }
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      }
    },

    async fetchCurrentUrl () {
      try {
        const { data } = await axios.get(import.meta.env.VITE_API_URL + '/current-url');
        this.currentUrl = data.current_url || null;
      } catch (error) {
        console.error('Failed to fetch current URL:', error);
        this.currentUrl = null;
      }
    },

    setStatus (process, status) {
      if (this.statuses.hasOwnProperty(process)) {
        this.statuses[process] = status;
      } else {
        console.error(`Invalid process name: ${process}`);
      }
    },

    startPolling () {
      if (this.pollingIntervalId !== null) return;

      this.urlIntervalId = setInterval(() => {
        this.fetchCurrentUrl();
      }, 1000);

      this.pollingIntervalId = setInterval(() => {
        this.checkStatus();
      }, 1000);
    },

    async startAcquisition (url) {
      try {
        await axios.post(import.meta.env.VITE_API_URL + '/start', { url });
        this.statuses.acquisition = 'in_progress';
        this.statuses.differentiation = 'not_started';
        this.statuses.summary = 'not_started';

        this.startPolling();
      } catch (error) {
        console.error('Failed to start acquisition:', error);
      }
    },

    stopPolling () {
      if (this.pollingIntervalId !== null) {
        clearInterval(this.pollingIntervalId);
        this.pollingIntervalId = null;
      }
    }
  },
});