import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import Home from './views/Home.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia } from 'pinia';

const router = createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        component: Home
      },
      {
        path: '/summary',
        component: () => import('./views/Summary.vue')
      },
      {
        path: '/finished',
        component: () => import('./views/Finished.vue')
      }
    ]
  }
);

const app = createApp(App);

const pinia = createPinia();

app.use(pinia);
app.use(router);

app.mount('#app');
