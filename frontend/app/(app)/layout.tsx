import BottomNav from "@/components/BottomNav";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto min-h-dvh max-w-md bg-smoke">
      <div className="px-5 pb-28 pt-12">{children}</div>
      <BottomNav />
    </div>
  );
}
