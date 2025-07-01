<template>
    <div class="box">
    <h2 class="title">{{ title }}</h2>
    <div class="current">
      {{ current }}
      <span v-if="hasPast" class="arrow" :class="{ 'up': current > past, 'down': current <= past }">
        <Icon :icon="current > past ? 'mdi:arrow-up' : 'mdi:arrow-down'" />
      </span>
    </div>
    <p v-if="hasPast" class="percentage">
      {{ percentageDifference }}% 
    </p>
    <footer v-if="footerTitle" class="footer">
      {{ footerTitle }}
    </footer>
  </div>

</template>

<script>
import {Icon} from '@iconify/vue';
import { number } from 'motion-v';

export default{
    components:{
        Icon
    },
    props:{
        title: {
            type:Object,
            required:true
        },
        current:{
            type:Number,
            required:true
        },
        past :{
            type:Number,
        },
        footerTitle :{
            type:Object
        }

    },
    computed: {
    hasPast() {
      return this.past !== undefined && this.past !== null;
    },
    percentageDifference() {
      if (!this.hasPast || this.past === 0) return 0;
      const diff = ((this.current - this.past) / this.past) * 100;
      return diff.toFixed(2); 
    },
  },
}
</script>

<style scoped>

.box {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  max-width: 200px;
}

.title {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.current {
  font-size: 2rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.arrow {
  font-size: 1.5rem;
}

.arrow.up {
  color: red;
}

.arrow.down {
  color: green;
}

.percentage {
  font-size: 1rem;
  margin-top: 0.5rem;
}

.footer {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #6c757d;
}
</style>