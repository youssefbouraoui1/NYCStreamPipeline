<script setup>
import { ref } from 'vue'; 
import HelloWorld from './components/HelloWorld.vue'
import Sidebar from './components/Sidebar.vue';
import General from './pages/accidents/General.vue';

const sidebarOpen = ref(true);
const darkMode = ref(false);
</script>

<template>
  <div :class="['app-layout', { 'dark-theme': darkMode }]">
    <Sidebar :isOpen="sidebarOpen" @toggle="sidebarOpen = !sidebarOpen" />
    <main :class="{ 'full-width': !sidebarOpen }" class="main-content">
      <button @click="darkMode = !darkMode" class="theme-toggle">
        {{ darkMode ? 'Light Mode' : 'Dark Mode' }}
      </button>

      

      <router-view />
    </main>

  </div>
</template>

<style scoped>
.app-layout{
  display: flex;
}

.sidebar {
  flex-shrink: 0; 
}

.full-width{
  width: 100%;
}

.main-content {
  flex-grow: 1; 
  overflow-y: auto; 
  padding: 1rem; 
  background: var(--bg-color);
  color: var(--text-color);
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
