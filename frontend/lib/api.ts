import type { Phase } from "@/lib/mock";

// Set NEXT_PUBLIC_API_URL to the deployed backend; it's baked in at build time.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Club = "driver" | "iron";

export type Analysis = {
  id: string;
  club: string;
  score: number;
  topIssue: string;
  strengths: string[];
  needsWork: string[];
  phases: Phase[];
  videoUrl: string;
};

export async function analyzeSwing(video: File, club: Club): Promise<Analysis> {
  const body = new FormData();
  body.append("video", video);
  body.append("club", club);

  let response: Response;
  try {
    response = await fetch(`${API_URL}/analyze`, { method: "POST", body });
  } catch {
    throw new Error("Couldn't reach the analysis server. Check your connection and try again.");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      typeof error?.detail === "string" ? error.detail : "Something went wrong analyzing your swing."
    );
  }

  const analysis: Analysis = await response.json();
  return { ...analysis, videoUrl: `${API_URL}${analysis.videoUrl}` };
}
