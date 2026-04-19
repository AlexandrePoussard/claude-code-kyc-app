<script setup lang="ts">
import { computed } from "vue";
import { Line } from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";
import { palette } from "../../charts";
import type { DailyCount } from "../../types";

const props = defineProps<{ series: DailyCount[] }>();

const chartData = computed<ChartData<"line">>(() => ({
  labels: props.series.map((d) => d.date),
  datasets: [
    {
      label: "Submissions",
      data: props.series.map((d) => d.count),
      borderColor: palette.primary,
      backgroundColor: palette.primarySoft,
      fill: true,
      tension: 0.35,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2,
    },
  ],
}));

const options: ChartOptions<"line"> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      displayColors: false,
      callbacks: {
        title: (items) => new Date(items[0].label).toLocaleDateString(),
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        autoSkip: true,
        maxTicksLimit: 6,
        callback: function (value) {
          const raw = this.getLabelForValue(Number(value));
          const d = new Date(raw);
          return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
        },
      },
    },
    y: { beginAtZero: true, ticks: { precision: 0 } },
  },
};
</script>

<template>
  <div class="chart-wrap">
    <Line :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap { height: 220px; position: relative; }
</style>
