<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { palette } from "../../charts";
import type { ReviewerStatsEntry } from "../../types";

const props = defineProps<{ reviewers: ReviewerStatsEntry[] }>();

const chartData = computed<ChartData<"bar">>(() => ({
  labels: props.reviewers.map((r) => r.reviewer),
  datasets: [
    {
      label: "Approved",
      data: props.reviewers.map((r) => r.approved),
      backgroundColor: palette.success,
      borderRadius: 4,
      stack: "decisions",
    },
    {
      label: "Rejected",
      data: props.reviewers.map((r) => r.rejected),
      backgroundColor: palette.danger,
      borderRadius: 4,
      stack: "decisions",
    },
  ],
}));

const options: ChartOptions<"bar"> = {
  indexAxis: "y",
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: "top" }, tooltip: { displayColors: true } },
  scales: {
    x: { beginAtZero: true, stacked: true, ticks: { precision: 0 } },
    y: { stacked: true },
  },
};
</script>

<template>
  <div v-if="reviewers.length === 0" class="muted">No decisions recorded yet.</div>
  <div v-else class="chart-wrap">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 240px; position: relative; }
</style>
