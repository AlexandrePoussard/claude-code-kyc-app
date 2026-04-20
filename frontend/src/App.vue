<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo" aria-hidden="true">
          <!-- classic bank facade: columns + pediment + steps -->
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M12 2 1 7v2h22V7L12 2zm-8 8v8h2v-8H4zm5 0v8h2v-8H9zm4 0v8h2v-8h-2zm6 0v8h2v-8h-2zM1 20v2h22v-2H1z"/>
          </svg>
        </div>
        <div class="brand-text">
          <div class="title">Meridian Private Bank</div>
          <div class="subtitle">Client Onboarding Console</div>
        </div>
      </div>
      <nav>
        <RouterLink to="/">Overview</RouterLink>
        <RouterLink to="/kyc">KYC</RouterLink>
        <RouterLink to="/accounts">Account creation</RouterLink>
        <RouterLink to="/rm">Relationship manager</RouterLink>
        <RouterLink to="/onboarding">New client</RouterLink>
        <RouterLink to="/audit">Audit</RouterLink>
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
.brand { display: flex; align-items: center; gap: 12px; }
.logo {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a, #312e81);
  color: #ffffff;
  box-shadow: 0 2px 8px -2px rgba(30, 58, 138, 0.4);
}
.brand-text { line-height: 1.2; }
.brand-text .title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
}
.brand-text .subtitle {
  font-size: 12px;
  color: var(--muted);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-weight: 600;
}
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
