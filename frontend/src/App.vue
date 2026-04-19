<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="logo">KYC</span>
        <span class="title">Workshop Console</span>
      </div>
      <nav>
        <RouterLink to="/dashboard">Reviewer dashboard</RouterLink>
        <RouterLink to="/analytics">Analytics</RouterLink>
        <RouterLink to="/onboarding">New application</RouterLink>
        <RouterLink to="/audit">Audit log</RouterLink>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 10px; }
.logo {
  background: var(--primary);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 700;
  letter-spacing: 0.05em;
  font-size: 14px;
}
.title { font-size: 18px; font-weight: 600; }
nav { display: flex; gap: 18px; }
nav a {
  color: var(--muted);
  font-weight: 500;
  font-size: 14px;
  padding: 6px 0;
  border-bottom: 2px solid transparent;
}
nav a:hover { text-decoration: none; color: var(--text); }
nav a.router-link-active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}
</style>
