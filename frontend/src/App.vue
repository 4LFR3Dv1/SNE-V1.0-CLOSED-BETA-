<template>
  <div id="app">
    <Header />
    <div class="container mx-auto px-4 py-8">
      <router-view />
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Header from './components/common/Header.vue'
import Footer from './components/common/Footer.vue'
</script>

<style>
#app {
  min-height: 100vh;
  background: #000000;
}
</style>

