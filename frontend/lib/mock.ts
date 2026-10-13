import { notFound } from "next/navigation";

// Placeholder data until the frontend is wired to the FastAPI backend.
// latestSwing uses real values from backend/swing_angles_data/swing_vs_pro_feedback.json.

export type Metric = {
  label: string;
  value: number;
  unit: string;
  proAvg: number;
  proStd: number;
  status: "good" | "warn";
  note?: string | null;
};

export type Phase = {
  key: string;
  name: string;
  score: number;
  metrics: Metric[];
};

export type Swing = {
  id: string;
  date: string;
  club: "Driver" | "Iron";
  score: number;
  topIssue: string;
  strengths: string[];
  needsWork: string[];
  phases: Phase[];
};

export type User = {
  name: string;
  handedness: "Right" | "Left";
  skill: "Beginner" | "Intermediate" | "Advanced";
  club: "Driver" | "Iron";
};

export const user: User = {
  name: "Evan",
  handedness: "Right",
  skill: "Intermediate",
  club: "Driver",
};

export function scoreColor(score: number): string {
  if (score >= 80) return "var(--color-good)";
  if (score >= 60) return "var(--color-brand)";
  return "var(--color-warn)";
}

const deg = "°";

export const latestSwing: Swing = {
  id: "s5",
  date: "Oct 12",
  club: "Driver",
  score: 72,
  topIssue: "Lead arm bends at the top of the backswing",
  strengths: [
    "Spine angle holds steady through the swing",
    "Good hip extension at the top",
    "Shoulder turn within pro range at the top",
  ],
  needsWork: [
    "Lead arm bends more than pros at the top",
    "Hips over-rotate at the top",
    "Not enough knee flex at setup",
  ],
  phases: [
    {
      key: "setup",
      name: "Setup",
      score: 78,
      metrics: [
        { label: "Spine angle", value: 28, unit: deg, proAvg: 25, proStd: 10, status: "good" },
        { label: "Knee bend", value: 12, unit: deg, proAvg: 24, proStd: 10, status: "warn", note: "Add knee flex" },
      ],
    },
    {
      key: "top_of_backswing",
      name: "Top of Backswing",
      score: 64,
      metrics: [
        { label: "Lead arm angle", value: 81, unit: deg, proAvg: 112, proStd: 22, status: "warn", note: "Keep lead arm longer" },
        { label: "Hip rotation", value: 11, unit: deg, proAvg: 5, proStd: 2, status: "warn", note: "Quieter lower body" },
        { label: "X-factor", value: 5, unit: deg, proAvg: 8, proStd: 5, status: "good" },
      ],
    },
    {
      key: "impact",
      name: "Impact",
      score: 70,
      metrics: [
        { label: "Spine angle", value: 7, unit: deg, proAvg: 19, proStd: 13, status: "good" },
        { label: "Hip angle", value: 172, unit: deg, proAvg: 149, proStd: 17, status: "warn", note: "Early extension" },
      ],
    },
  ],
};

export const swings: Swing[] = [
  latestSwing,
  {
    id: "s4",
    date: "Oct 8",
    club: "Iron",
    score: 68,
    topIssue: "Early extension through impact",
    strengths: ["Solid setup posture"],
    needsWork: ["Hips thrust toward the ball at impact"],
    phases: [],
  },
  {
    id: "s3",
    date: "Oct 3",
    club: "Driver",
    score: 63,
    topIssue: "Limited shoulder turn",
    strengths: ["Balanced finish"],
    needsWork: ["Shoulders and hips turn together"],
    phases: [],
  },
  {
    id: "s2",
    date: "Sep 27",
    club: "Iron",
    score: 59,
    topIssue: "Loss of posture in the downswing",
    strengths: [],
    needsWork: ["Spine angle changes in transition"],
    phases: [],
  },
  {
    id: "s1",
    date: "Sep 20",
    club: "Driver",
    score: 54,
    topIssue: "Lead arm collapses at the top",
    strengths: [],
    needsWork: ["Lead arm bends at the top", "Little knee flex at setup"],
    phases: [],
  },
];

export function getSwing(id: string): Swing {
  return swings.find((s) => s.id === id) ?? notFound();
}

export const recentProgress = [
  { label: "Lead arm at top", from: 68, to: 81, unit: deg },
  { label: "Setup knee bend", from: 6, to: 12, unit: deg },
  { label: "Overall score", from: 54, to: 72, unit: "" },
];
