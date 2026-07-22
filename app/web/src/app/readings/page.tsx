import { Suspense } from "react";
import { AppShell } from "@/components/app-shell";
import { ReadingsClient } from "@/components/readings-client";
import { SkeletonBlock } from "@/components/glicovia-ui";

export default function ReadingsPage() {
  return (
    <AppShell>
      <Suspense fallback={<SkeletonBlock className="h-[560px]" />}>
        <ReadingsClient />
      </Suspense>
    </AppShell>
  );
}
