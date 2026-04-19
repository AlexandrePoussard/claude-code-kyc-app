<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { palette } from "../../charts";
import type { CountryCount } from "../../types";

const props = defineProps<{ countries: CountryCount[] }>();

const chartData = computed<ChartData<"bar">>(() => ({
  labels: props.countries.map((c) => c.country),
  datasets: [
    {
      label: "Applications",
      data: props.countries.map((c) => c.count),
      backgroundColor: palette.info,
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
  <div v-if="countries.length === 0" class="muted">No applications yet.</div>
  <div v-else class="chart-wrap">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 280px; position: relative; }
</style>
