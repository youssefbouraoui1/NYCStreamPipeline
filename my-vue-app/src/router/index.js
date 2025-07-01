import { createRouter, createWebHistory } from 'vue-router'

import General from '../pages/accidents/General.vue'
import Factors from '../pages/accidents/Factors.vue'
import Vehicles from '../pages/accidents/Vehicles.vue'
import Borough from '../pages/accidents/Borough.vue'
//import InjuredKilled from '../views/InjuredKilled.vue'
import Reports from '../pages/reports/Reports.vue'

const routes = [
  { path: '/', redirect: '/general' },
  { path: '/general', component: General },
  { path: '/factors', component: Factors },
  { path: '/vehicles', component: Vehicles },
  { path: '/borough', component: Borough },
  //{ path: '/injured-killed', component: InjuredKilled },
  { path: '/reports', component: Reports },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
