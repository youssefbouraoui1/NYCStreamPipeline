<script setup>
import { ref } from 'vue'; 
import Sidebar from './components/Sidebar.vue';

const sidebarOpen = ref(true);
const darkMode = ref(false);
</script>

<template>
  <div :class="['app-layout', { 'dark-theme': darkMode }]">
    <Sidebar :isOpen="sidebarOpen" @toggle="sidebarOpen = !sidebarOpen" />
    <main :class="[{ 'sidebar-closed': !sidebarOpen }, 'main-content']">
      <button @click="darkMode = !darkMode" class="theme-toggle">
        {{ darkMode ? 'Light Mode' : 'Dark Mode' }}
      </button>

      

      <router-view />
    </main>

  </div>
</template>

<style scoped>
:root {
  --bg-color: #f5f6fa;
  --text-color: #222;
  --card-bg: #fff;
  --sidebar-bg: #888888;
  --sidebar-text: #222;
}

.main-content {
  margin-left: 250px;
  transition: margin-left 0.3s;
  overflow-y: auto;
  padding: 1rem;
  height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
}
.sidebar-closed {
  margin-left: 50px;
}
.theme-toggle {
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  z-index: 3000;
  position: relative;
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
.app-layout {
  background: var(--bg-color, #18191a);
  min-height: 100vh;
  width: 100vw;
  transition: background 0.3s;
}
</style>
