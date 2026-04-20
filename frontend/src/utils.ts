import type { AccountType, Application } from "./types";

/** Years between a date-of-birth string and today. */
export function ageFrom(dob: string): number {
  const d = new Date(dob);
  const today = new Date();
  let years = today.getFullYear() - d.getFullYear();
  const mDiff = today.getMonth() - d.getMonth();
  if (mDiff < 0 || (mDiff === 0 && today.getDate() < d.getDate())) years -= 1;
  return years;
}

export function daysSince(iso: string): number {
  const then = new Date(iso).getTime();
  const now = Date.now();
  return Math.max(0, Math.floor((now - then) / (1000 * 60 * 60 * 24)));
}

export interface AccountSuggestion {
  type: AccountType;
  reason: string;
}

/**
 * Basic heuristic for proposing an account product after KYC approval.
 *
 * High-risk clients default to a plain checking account so the bank has the
 * least exposure. Young adults are pushed to savings. Older / mature low-risk
 * clients get the investment pitch by default. This mirrors the kind of rule
 * you would see in a real on-boarding script; tweak freely in workshops.
 */
export function suggestAccountType(app: Application): AccountSuggestion {
  if (app.risk?.level === "high") {
    return { type: "checking", reason: "High-risk profile — start with plain checking." };
  }
  const age = ageFrom(app.applicant.date_of_birth);
  if (age < 25) {
    return { type: "savings", reason: "Client under 25 — savings is the usual entry product." };
  }
  if (app.applicant.politically_exposed) {
    return { type: "checking", reason: "PEP — keep product simple until EDD clears." };
  }
  if (app.risk?.level === "medium") {
    return { type: "savings", reason: "Medium-risk profile — savings pairs with wealth advisor." };
  }
  return { type: "investment", reason: "Low-risk mature client — investment is the default upsell." };
}
