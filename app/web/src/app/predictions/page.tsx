import { Suspense } from "react";
import { AppShell } from "@/components/app-shell";
import { PredictionsClient } from "@/components/predictions-client";
import { SkeletonBlock } from "@/components/glicovia-ui";

export default function PredictionsPage() {
  return (
    <AppShell>
      <Suspense fallback={<SkeletonBlock className="h-[560px]" />}>
        <PredictionsClient />
      </Suspense>
    </AppShell>
  );
}
