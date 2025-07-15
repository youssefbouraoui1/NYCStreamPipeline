<template>
    <div>
        <div class="boxes">
            <BoxInfo 
            v-for="(box, index) in boxesData" 
            :key="index"
            :title="box.title" 
            :current="box.current" 
            :past="box.past" 
            :footerTitle="box.footer" 
            />
        </div>
        <div class="lineCharts">
            <div class="lineChartBox">
            <span>
                Number Of Accidents Over time
            </span>
            <Linechart
               v-if="lineChartData"
               :chartData="lineChartData"
             />
             </div>
            
        </div>
    </div>

</template>

<script setup>
  import { ref, onMounted } from 'vue';
  import Linechart from '../../components/charts/Linechart.vue';
  import BoxInfo from '../../components/charts/BoxInfo.vue';
  import { fecthAccidentCountInjuredAndKilledOverTime, fetchAccidentsCount,fetchInjuriesCount,fetchKilledCount,fetchPeakTime } from '../../services/GeneralStatisticsServices';
  
  const boxesData = ref([]);
  const lineChartData = ref(null);

  onMounted(async()=>{

    try{
        const [accidents,injuries,killed,peak,lineData] = await Promise.all([
            fetchAccidentsCount(),
            fetchInjuriesCount(),
            fetchKilledCount(),
            fetchPeakTime(),
            fecthAccidentCountInjuredAndKilledOverTime()
        ]);

        boxesData.value = [
            {title:'Accidents Count',current:accidents.current,past:accidents.past, footer: 'Compared to last month'},
            {title:'Injuries Count',current:injuries.current,past:injuries.past, footer: 'Compared to last month'},
            {title:'Accidents Count',current:killed.current,past:killed.past, footer: 'Compared to last month'},
            {title:'Accidents Peak Time',current:peak.current,past:peak.past, footer: 'Compared to last month'}
        ];

        lineChartData.value=lineData

    }catch(error){
        console.error('Error fetching box data:', error);
    }
  })

</script>

<style scoped>

.boxes {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap:1rem;
    max-width: 1400px;
    margin: 0 auto;
}

.lineCharts{
    display: grid;
    grid-template-columns: repeat(1,1fr);
    gap: 1rem;
    margin-top: 10px;
}

.lineChartBox{
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
</style>