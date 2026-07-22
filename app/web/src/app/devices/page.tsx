import { AppShell } from "@/components/app-shell";
import { DevicesClient } from "@/components/devices-client";

export default function DevicesPage() {
  return (
    <AppShell>
      <DevicesClient />
    </AppShell>
  );
}
