<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

export default {
  name: 'LineChart',
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
  components: {
    Line
  },
  mounted() {
    this.renderChart()
  },
  methods: {
    renderChart() {
      const context = this.$refs.chartCanvas.getContext('2d')
      new ChartJS(context, {
        type: 'line',
        data: this.chartData,
        options: this.chartOptions
      })
    }
  }
}
</script>

<style scoped>
/* Optional styles for the chart container */
</style>
