<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { palette } from "../../charts";
import type { FunnelSteps } from "../../types";

const props = defineProps<{ funnel: FunnelSteps }>();

const chartData = computed<ChartData<"bar">>(() => ({
  labels: ["Submitted", "Documents uploaded", "Decided", "Approved"],
  datasets: [
    {
      label: "Applications",
      data: [
        props.funnel.submitted,
        props.funnel.documents_uploaded,
        props.funnel.decided,
        props.funnel.approved,
      ],
      backgroundColor: [palette.info, palette.primary, palette.warn, palette.success],
      borderRadius: 6,
      maxBarThickness: 36,
    },
  ],
}));

const options: ChartOptions<"bar"> = {
  indexAxis: "y",
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { displayColors: false },
  },
  scales: {
    x: { beginAtZero: true, ticks: { precision: 0 } },
  },
};
</script>

<template>
  <div class="chart-wrap" style="height: 240px">
    <Bar :data="chartData" :options="options" />
  </div>
</template>
