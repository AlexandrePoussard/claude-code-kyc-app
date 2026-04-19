import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Filler,
);

ChartJS.defaults.font.family =
  '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
ChartJS.defaults.color = "#4b5563";
ChartJS.defaults.borderColor = "rgba(148, 163, 184, 0.2)";

export const palette = {
  primary: "#6366f1",
  primarySoft: "rgba(99, 102, 241, 0.15)",
  success: "#10b981",
  successSoft: "rgba(16, 185, 129, 0.18)",
  warn: "#f59e0b",
  warnSoft: "rgba(245, 158, 11, 0.18)",
  danger: "#ef4444",
  dangerSoft: "rgba(239, 68, 68, 0.15)",
  info: "#06b6d4",
  infoSoft: "rgba(6, 182, 212, 0.15)",
  muted: "#94a3b8",
};

export const statusColor: Record<string, string> = {
  pending: palette.info,
  in_review: palette.warn,
  approved: palette.success,
  rejected: palette.danger,
};

export const riskColor: Record<string, string> = {
  low: palette.success,
  medium: palette.warn,
  high: palette.danger,
};
