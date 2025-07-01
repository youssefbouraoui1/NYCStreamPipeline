<template>
  <div>
    <div    @click="$emit('toggle')" aria-label="Toggle sidebar">
      <Icon icon="mdi:menu" class="hamburger" />
    </div>
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
      type: Boolan,
      required: true,
    }
  }
}
</script>

<style scoped>


</style>
