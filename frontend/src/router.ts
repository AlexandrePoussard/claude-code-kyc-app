import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "overview", component: () => import("./views/OverviewView.vue") },
    { path: "/kyc", name: "kyc", component: () => import("./views/KycQueueView.vue") },
    { path: "/accounts", name: "accounts", component: () => import("./views/AccountQueueView.vue") },
    { path: "/rm", name: "rm", component: () => import("./views/RmQueueView.vue") },
    { path: "/onboarding", name: "onboarding", component: () => import("./views/OnboardingView.vue") },
    { path: "/applications/:id", name: "application-detail", component: () => import("./views/ApplicationDetailView.vue"), props: true },
    { path: "/audit", name: "audit", component: () => import("./views/AuditView.vue") },
    // Legacy redirects
    { path: "/dashboard", redirect: "/kyc" },
    { path: "/analytics", redirect: "/" },
  ],
});
