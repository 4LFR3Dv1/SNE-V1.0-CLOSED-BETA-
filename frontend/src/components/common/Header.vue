<template>
  <header class="bg-terminal-gray border-b border-terminal-green">
    <div class="container mx-auto px-4 py-4">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-2xl font-bold text-terminal-green hover:opacity-80 transition">
            🚀 SNE RADAR
          </router-link>
          <span class="text-sm text-terminal-green/70 hidden md:block">
            Sistema Neural Estratégico
          </span>
        </div>

        <!-- Navigation -->
        <nav class="flex space-x-4">
          <router-link 
            to="/" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            Dashboard
          </router-link>
          <router-link 
            to="/analysis" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            Análise
          </router-link>
          <router-link 
            to="/wick-radar" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            🎯 Wick Radar
          </router-link>
          <router-link 
            to="/automated-trading" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            🏦 Trading Automatizado
          </router-link>
          <router-link 
            to="/magnetic" 
            class="px-4 py-2 hover:text-terminal-green transition hidden md:block"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            Campo Magnético
          </router-link>
        </nav>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <span class="text-sm text-terminal-green/70 hidden sm:block">
            {{ userStore.username || 'Usuário' }}
          </span>
          <button 
            @click="logout"
            class="px-4 py-2 bg-red-500/20 text-red-500 rounded hover:bg-red-500/30 transition"
          >
            Sair
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const logout = () => {
  userStore.logout()
  router.push('/')
}
</script>

