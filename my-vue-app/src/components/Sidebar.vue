<template>
  <div class="sidebar-wrapper">
    <nav :class="['sidebar', { closed: !isOpen }]">
      <div @click="$emit('toggle')" aria-label="Toggle sidebar">
        <Icon icon="mdi:menu" class="hamburger" />
      </div>
      <ul v-if="isOpen">
        <li>
          <div @click="toggleDropdown('accidents')" class="dropdown-title">
            Accidents
            <span>{{ dropdowns.accidents ? '▲' : '▼' }}</span>
          </div>
          <ul v-show="dropdowns.accidents" class="submenu">
            <li><router-link to="/general">General</router-link></li>
            <li><router-link to="/factors">Factors</router-link></li>
            <li><router-link to="/vehicles">Vehicles</router-link></li>
            <li><router-link to="/borough">Borough & Street</router-link></li>
            <li><router-link to="/injured-killed">Injured & Killed</router-link></li>
          </ul>
        </li>

        <li><router-link to="/general">Reports</router-link></li>
      </ul>
    </nav>
  </div>


</template>

<script>
import { Icon } from '@iconify/vue';
export default {
  components: {
    Icon,
  },

  props: {
    isOpen: {
      type: Boolean,
      required: true,
    }
  },
  data() {
    return {
      dropdowns: {
        accidents: false,
        reports: false,
      }
    }
  },
  methods: {
    toggleDropdown(name) {
      this.dropdowns[name] = !this.dropdowns[name]
    }
  }
}
</script>

<style scoped>
.sidebar-wrapper {
  position: fixed;
  width: 250px;
  height: 100vh;
  padding-right: 10px;
}

.sidebar {
  width: 250px;
  background: var(--sidebar-bg, #18191a);
  height: 100vh;
  color: var(--sidebar-text);
  padding: 1rem;
  position: 10px;
  transition: transform 0.3s ease;
  overflow: hidden;
}

.closed {
  transform: translateX(-80%);

}

.hamburger {
  position: absolute;
  top: 1rem;
  right: 10px;
  width: 35px;
  height: 35px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: var(--sidebar-text);
  z-index: 10;
}

ul {
  margin-top: 4rem;
  list-style: none;
  padding: 0;
}

a {
  color: var(--sidebar-text);
  text-decoration: none;
}
</style>
