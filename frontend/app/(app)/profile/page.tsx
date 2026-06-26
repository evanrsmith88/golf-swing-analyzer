"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, SectionTitle } from "@/components/ui";
import { SettingsIcon, LogoutIcon, TrophyIcon } from "@/components/icons";
import { user } from "@/lib/mock";

function Segmented<T extends string>({
  options,
  value,
  onChange,
}: {
  options: readonly T[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="flex gap-1 rounded-2xl bg-smoke p-1">
      {options.map((opt) => {
        const active = opt === value;
        return (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={`flex-1 rounded-xl py-2.5 text-sm font-medium transition ${
              active
                ? "bg-brand text-white shadow-sm"
                : "text-muted hover:text-ink"
            }`}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

export default function ProfilePage() {
  const [name, setName] = useState(user.name);
  const [hand, setHand] = useState<"Right" | "Left">(user.handedness);
  const [skill, setSkill] = useState<
    "Beginner" | "Intermediate" | "Advanced"
  >(user.skill);
  const [club, setClub] = useState<"Driver" | "Iron">(user.club);

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
          Profile
        </h1>
      </header>

      {/* Avatar header */}
      <Card className="flex items-center gap-4">
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-brand font-display text-2xl font-bold text-white">
          {name.charAt(0).toUpperCase()}
        </span>
        <div>
          <p className="font-display text-xl font-semibold text-ink">{name}</p>
          <p className="flex items-center gap-1 text-sm text-muted">
            <TrophyIcon className="h-4 w-4" />
            {skill} · {hand}-handed
          </p>
        </div>
      </Card>

      {/* Name */}
      <section>
        <SectionTitle>Name</SectionTitle>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="h-13 w-full rounded-2xl border border-line bg-white px-4 py-3.5 text-ink outline-none focus:border-brand"
        />
      </section>

      {/* Handedness */}
      <section>
        <SectionTitle>Handedness</SectionTitle>
        <Segmented
          options={["Right", "Left"] as const}
          value={hand}
          onChange={setHand}
        />
      </section>

      {/* Skill level */}
      <section>
        <SectionTitle>Skill Level</SectionTitle>
        <Segmented
          options={["Beginner", "Intermediate", "Advanced"] as const}
          value={skill}
          onChange={setSkill}
        />
      </section>

      {/* Preferred club */}
      <section>
        <SectionTitle>Preferred Club</SectionTitle>
        <Segmented
          options={["Driver", "Iron"] as const}
          value={club}
          onChange={setClub}
        />
      </section>

      {/* Settings & logout */}
      <section className="mt-2 flex flex-col gap-3">
        <button className="flex items-center gap-3 rounded-[var(--radius-card)] border border-line bg-white px-5 py-4 text-left text-sm font-medium text-ink transition active:scale-[0.99]">
          <SettingsIcon className="h-5 w-5 text-muted" />
          Settings
        </button>
        <Link
          href="/"
          className="flex items-center gap-3 rounded-[var(--radius-card)] border border-line bg-white px-5 py-4 text-sm font-medium text-warn transition active:scale-[0.99]"
        >
          <LogoutIcon className="h-5 w-5" />
          Log out
        </Link>
      </section>

      <p className="pb-2 text-center text-xs text-muted">SwingLabs v1.0</p>
    </div>
  );
}
