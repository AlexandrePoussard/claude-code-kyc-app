<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { statusColor } from "../../charts";
import type { StatusCounts } from "../../types";

const props = defineProps<{ counts: StatusCounts }>();

const chartData = computed<ChartData<"bar">>(() => ({
  labels: ["Pending", "In review", "Approved", "Rejected"],
  datasets: [
    {
      label: "Applications",
      data: [
        props.counts.pending,
        props.counts.in_review,
        props.counts.approved,
        props.counts.rejected,
      ],
      backgroundColor: [
        statusColor.pending,
        statusColor.in_review,
        statusColor.approved,
        statusColor.rejected,
      ],
      borderRadius: 6,
      maxBarThickness: 40,
    },
  ],
}));

const options: ChartOptions<"bar"> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { displayColors: false },
  },
  scales: {
    y: { beginAtZero: true, ticks: { precision: 0 } },
  },
};
</script>

<template>
  <div class="chart-wrap">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 220px; position: relative; }
</style>
