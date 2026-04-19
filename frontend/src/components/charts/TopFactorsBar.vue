<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { palette } from "../../charts";
import type { FactorCount } from "../../types";

const props = defineProps<{ factors: FactorCount[] }>();

const chartData = computed<ChartData<"bar">>(() => ({
  labels: props.factors.map((f) => f.label),
  datasets: [
    {
      label: "Times triggered",
      data: props.factors.map((f) => f.count),
      backgroundColor: palette.warn,
      borderRadius: 4,
      maxBarThickness: 24,
    },
  ],
}));

const options: ChartOptions<"bar"> = {
  indexAxis: "y",
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { displayColors: false } },
  scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
};
</script>

<template>
  <div v-if="factors.length === 0" class="muted">No factors triggered yet.</div>
  <div v-else class="chart-wrap">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 280px; position: relative; }
</style>
