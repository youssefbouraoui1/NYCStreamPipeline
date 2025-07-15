<template>
  <div class="box">
    <h2 class="title"><strong>{{ title }}</strong></h2>
    <div class="current">
      {{ currentFactor }}
    </div>
    <div class="accidentNumber">
      <p>Number of Accidents: </p> {{ currentFactorAccidentsCount }}
    </div>

  </div>

</template>

<script>
import { Icon } from '@iconify/vue';

export default {
  components: {
    Icon
  },
  props: {
    title: {
      type: String,
      required: true
    },
    currentFactor: {
      type: String,
      required: true
    },
    currentFactorAccidentsCount: {
      type: Number,
      required: true
    },

  },
  computed: {
    hasPast() {
      return this.past !== undefined && this.past !== null;
    },
    percentageDifference() {
      if (!this.hasPast || this.past === 0) return 0;
      if (typeof (this.current) === 'string') {
        return this.past;
      } else {
        const diff = ((this.current - this.past) / this.past) * 100;
        return diff.toFixed(2);
      }
    },
  },
}
</script>

<style scoped>
.box {
  background-color: 
#f8f9fa;
  border: 1px solid 
#dee2e6;
  
  padding: 1rem;

  text-align: center;
  max-width: 340px;

}

.title {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.current {
  font-size: 1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.accidentNumber{
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: red;
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
  color: 
#6c757d;
}
</style>