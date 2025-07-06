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
        options: {
      responsive: true,
      maintainAspectRatio: false,
      ...this.chartOptions
    }
      })
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 100%;
  height: 400px;      
  position: relative;
  overflow-x: hidden; 
}

canvas {
  width: 101% !important;
  height: 500px !important;
  max-height: 500px;
  display: block;
}
</style>