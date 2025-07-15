<template>
    <div class="box">
        <div class="header">
            <span>
                {{ title }}
            </span>
            <div class="selectDropdown">

                <Dropdown v-model="selectedInterval" :options="intervals" optionLabel="name"
                    placeholder="Select an Interval" class="w-full md:w-14rem" />

                <Dropdown v-model="selectedFactor" :options="factors" optionLabel="name" placeholder="Select a Factor"
                    class="w-full md:w-14rem" />
            </div>
        </div>
        <div class="body">
            <Linechart v-if="chartData" :chartData="chartData" />
        </div>

    </div>

</template>

<script>
//the component will be improved so that on every click we render the data
import { Icon } from '@iconify/vue';
import Dropdown from 'primevue/dropdown';
import Linechart from './Linechart.vue';
import axios from 'axios';

const intervals = ['Month', '6 Months', 'Year', '2 Years'];
const factors = ['Passing Too Closely', 'Following Too Closely', 'Driver Inattention/Distraction']


export default {
    components: {
        Icon,
        Dropdown,
        Linechart
    },
    props: {
        title: {
            type: String,
            required: true
        },
    },
    data() {
        return {
            intervals: [
                { name: 'Month', value: '1m' },
                { name: '6 Months', value: '6m' },
                { name: 'Year', value: '1y' },
                { name: '2 Years', value: '2y' }
            ],
            factors: [
                { name: 'Passing Too Closely', value: 'passing' },
                { name: 'Following Too Closely', value: 'following' },
                { name: 'Driver Inattention/Distraction', value: 'inattention' }
            ],
            selectedInterval: null,
            selectedFactor: null,
            chartData: null
        };
    },
    watch: {
        selectedFactor: 'fetchChartData',
        selectedInterval: 'fetchChartData'
    },
    methods: {
        async fetchChartData() {
            if (!this.selectedInterval || !this.selectedFactor) return;

            const interval = this.selectedInterval.value;
            const factor = this.selectedFactor.value;

            try {
                const response = await axios.get(
                    `http://localhost:3000/api/data/${interval}/${factor}`
                );
                console.log("response: ",response)
                this.chartData = response.data;
            } catch (error) {
                console.error('Failed to fetch chart data:', error);
            }
        }
    }
}
</script>

<style scoped>
.box {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    
}

.title {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
}

.header {
    display: flex;
    justify-content: space-between;
}
.selectDropdown{
    display: inline-flex;
    gap : 10px;
}


</style>