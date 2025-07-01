<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'BarChart',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    chartOptions: {
      type: Object,
      default: () => ({})
    }
  },
  mounted() {
    this.renderChart()
  },
  methods: {
    renderChart() {
      const context = this.$refs.chartCanvas.getContext('2d')
      new ChartJS(context, {
        type: 'bar',
        data: this.chartData,
        options: this.chartOptions
      })
    }
  }
}
</script>

<style scoped>
</style>
