<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { palette } from "../../charts";
import type { ConfidenceBucket } from "../../types";

const props = defineProps<{ buckets: ConfidenceBucket[] }>();

const chartData = computed<ChartData<"bar">>(() => ({
  labels: props.buckets.map((b) => b.range),
  datasets: [
    {
      label: "Applicants",
      data: props.buckets.map((b) => b.count),
      backgroundColor: props.buckets.map((b) => {
        const [lo] = b.range.split("–").map(Number);
        if (lo < 0.7) return palette.danger;
        if (lo < 0.8) return palette.warn;
        return palette.success;
      }),
      borderRadius: 6,
      maxBarThickness: 40,
    },
  ],
}));

const options: ChartOptions<"bar"> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { displayColors: false } },
  scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
};
</script>

<template>
  <div class="chart-wrap">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 240px; position: relative; }
</style>
