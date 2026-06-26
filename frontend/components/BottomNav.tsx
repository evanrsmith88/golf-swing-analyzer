"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  HomeIcon,
  AnalyzeIcon,
  HistoryIcon,
  ProfileIcon,
} from "@/components/icons";

const tabs = [
  { href: "/home", label: "Home", Icon: HomeIcon },
  { href: "/analyze", label: "Analyze", Icon: AnalyzeIcon },
  { href: "/history", label: "History", Icon: HistoryIcon },
  { href: "/profile", label: "Profile", Icon: ProfileIcon },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 mx-auto max-w-md border-t border-line bg-white/95 backdrop-blur">
      <div className="grid grid-cols-4 px-2 pb-[max(8px,env(safe-area-inset-bottom))] pt-2">
        {tabs.map(({ href, label, Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className="flex flex-col items-center gap-1 rounded-xl py-1.5 transition-colors"
            >
              <Icon
                className={active ? "text-brand" : "text-muted"}
                strokeWidth={active ? 2.2 : 1.8}
              />
              <span
                className={`text-[11px] font-medium ${
                  active ? "text-brand" : "text-muted"
                }`}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
