<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";
import type { Stats } from "../types";
import FunnelBar from "../components/charts/FunnelBar.vue";
import TopFactorsBar from "../components/charts/TopFactorsBar.vue";
import TopCountriesBar from "../components/charts/TopCountriesBar.vue";
import LivenessHistogram from "../components/charts/LivenessHistogram.vue";
import ReviewerLeaderboard from "../components/charts/ReviewerLeaderboard.vue";

const stats = ref<Stats | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    stats.value = await api.getStats();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div v-if="loading" class="muted">Loading analytics…</div>
  <div v-else-if="stats" class="stack">
    <div class="row between">
      <h2 style="margin: 0">Analytics</h2>
      <button @click="load">Refresh</button>
    </div>

    <section class="panel">
      <h3>Review funnel</h3>
      <p class="muted">How applications progress from submission to approval.</p>
      <FunnelBar :funnel="stats.funnel" />
    </section>

    <div class="grid cols-2">
      <section class="panel">
        <h3>Top risk factors</h3>
        <p class="muted">Rules that fire most often across all applications.</p>
        <TopFactorsBar :factors="stats.top_risk_factors" />
      </section>

      <section class="panel">
        <h3>Top countries of residence</h3>
        <p class="muted">Where applicants are based (ISO-2 country codes).</p>
        <TopCountriesBar :countries="stats.top_countries" />
      </section>

      <section class="panel">
        <h3>Liveness confidence distribution</h3>
        <p class="muted">How confident the fake liveness check was, bucketed.</p>
        <LivenessHistogram :buckets="stats.liveness_confidence_buckets" />
      </section>

      <section class="panel">
        <h3>Reviewer leaderboard</h3>
        <p class="muted">Decisions per reviewer, split by outcome.</p>
        <ReviewerLeaderboard :reviewers="stats.reviewer_stats" />
      </section>
    </div>
  </div>
</template>

<style scoped>
h2 { font-size: 22px; }
h3 { margin: 0 0 4px; font-size: 16px; }
</style>
