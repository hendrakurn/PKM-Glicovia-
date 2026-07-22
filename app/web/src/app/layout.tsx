import type { Metadata } from "next";
import { JetBrains_Mono, Manrope } from "next/font/google";
import { AuthProvider } from "@/components/auth-provider";
import "./globals.css";

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  display: "swap",
});

const jetBrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "GLICOVIA Express",
  description: "Patient-first saliva glucose monitoring with device, reading, and model context.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${manrope.variable} ${jetBrainsMono.variable} h-full antialiased`}>
      <body className="min-h-[100dvh] bg-[color:var(--background)] text-[color:var(--ink)]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
