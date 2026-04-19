import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/onboarding", name: "onboarding", component: () => import("./views/OnboardingView.vue") },
    { path: "/dashboard", name: "dashboard", component: () => import("./views/DashboardView.vue") },
    { path: "/analytics", name: "analytics", component: () => import("./views/AnalyticsView.vue") },
    { path: "/applications/:id", name: "application-detail", component: () => import("./views/ApplicationDetailView.vue"), props: true },
    { path: "/audit", name: "audit", component: () => import("./views/AuditView.vue") },
  ],
});
