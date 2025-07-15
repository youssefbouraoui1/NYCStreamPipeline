<template>
  <div>
    <div class="boxFactors">
      <BoxFactors v-for="(fac, index) in factorAccidentCount" :key="index" :title="fac.title"
        :currentFactor="fac.currentFactor" :currentFactorAccidentsCount="fac.CFAC" />
    </div>
    <div class = "lineCharts">
    <!-- i willhave here number of accidents by factor over this year(we will let them choose the year or month or 2 year)
     we will have also an other chart of the peak time of accident and there factor -->
      <DropDownListLineChart title="Number Of Accidents By Factor"/>
      <PeakTimeChart title="Peak Time Per Factor"/>
    </div>
  </div>

</template>

<script setup>
import BoxFactors from '../../components/BoxFactors.vue';
import { ref, onMounted } from 'vue';
import {
  fetchaccidentCountOfTopFactorForTheDay, fetchaccidentCountOfTopFactorForTheMonth,
  fetchaccidentCountOfTopFactorForTheWeek, fetchaccidentCountOfTopFactorForTheYear
} from '../../services/FactorsService';
import DropDownListLineChart from '../../components/charts/DropDownListLineChart.vue';
import PeakTimeChart from './factors/components/PeakTimeChart.vue';

const factorAccidentCount = ref([]);
const err = ref({ happened: false, message: "" })

onMounted(async () => {
  try {

    const dayTopFactor = await fetchaccidentCountOfTopFactorForTheDay();
    const weekTopFactor = await fetchaccidentCountOfTopFactorForTheWeek();
    const monthTopFactor = await fetchaccidentCountOfTopFactorForTheMonth();
    const yearTopFactor = await fetchaccidentCountOfTopFactorForTheYear();

    factorAccidentCount.value = [
      { title: "Top Factor Of The Day", currentFactor: dayTopFactor.factorName, CFAC: dayTopFactor.accidentCount },
      { title: "Top Factor Of The Week", currentFactor: weekTopFactor.factorName, CFAC: weekTopFactor.accidentCount },
      { title: "Top Factor Of The Month", currentFactor: monthTopFactor.factorName, CFAC: monthTopFactor.accidentCount },
      { title: "Top Factor Of The Year", currentFactor: yearTopFactor.factorName, CFAC: yearTopFactor.accidentCount }
    ]

  } catch (error) {
    err.value.happened = true;
    err.value.message = error.message || String(error);
    console.error(error);
  }

})

defineOptions({
  name: 'Factors'
})
</script>

<style scoped>
.boxFactors{
  display: grid;
  grid-template-columns: repeat(4,1fr);
  grid-area: 10px;
}

.lineCharts{
  display: grid;
  grid-template-columns: repeat(2,1fr);
  gap:20px;
  margin-top: 20px;
  margin-right: 12px;
}
</style>
