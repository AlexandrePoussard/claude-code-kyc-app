<script setup lang="ts">
import { computed } from "vue";
import { Doughnut } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { riskColor } from "../../charts";
import type { RiskCounts } from "../../types";

const props = defineProps<{ counts: RiskCounts }>();

const chartData = computed<ChartData<"doughnut">>(() => ({
  labels: ["Low", "Medium", "High"],
  datasets: [
    {
      data: [props.counts.low, props.counts.medium, props.counts.high],
      backgroundColor: [riskColor.low, riskColor.medium, riskColor.high],
      borderWidth: 0,
      hoverOffset: 6,
    },
  ],
}));

const options: ChartOptions<"doughnut"> = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "62%",
  plugins: {
    legend: {
      position: "bottom",
      labels: { boxWidth: 10, boxHeight: 10, padding: 12 },
    },
    tooltip: { displayColors: false },
  },
};
</script>

<template>
  <div class="chart-wrap">
    <Doughnut :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 220px; position: relative; }
</style>
