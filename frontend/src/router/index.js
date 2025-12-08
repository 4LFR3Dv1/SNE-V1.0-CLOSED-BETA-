import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'
import Backtesting from '../views/Backtesting.vue'
import MagneticField from '../views/MagneticField.vue'
import Settings from '../views/Settings.vue'
import WickRadar from '../views/WickRadar.vue'
import AutomatedTrading from '../views/AutomatedTrading.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis
  },
  {
    path: '/backtesting',
    name: 'Backtesting',
    component: Backtesting
  },
  {
    path: '/magnetic',
    name: 'MagneticField',
    component: MagneticField
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/wick-radar',
    name: 'WickRadar',
    component: WickRadar
  },
  {
    path: '/automated-trading',
    name: 'AutomatedTrading',
    component: AutomatedTrading
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

