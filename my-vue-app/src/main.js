import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import 'primevue/resources/themes/saga-blue/theme.css';  // Choose your theme
import 'primevue/resources/primevue.min.css';            // Core styles
import 'primeicons/primeicons.css';   


createApp(App).use(router).use(PrimeVue).mount('#app')
