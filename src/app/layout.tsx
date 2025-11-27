import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DIO Platform - Digital Immune Organism Security Dashboard",
  description: "Advanced cybersecurity platform powered by AI-driven Digital Immune Organism technology for real-time threat detection and response.",
  keywords: ["DIO", "Digital Immune Organism", "cybersecurity", "AI security", "threat detection", "Next.js", "TypeScript"],
  authors: [{ name: "DIO Platform Team" }],
  icons: {
    icon: "/logo.svg",
  },
  openGraph: {
    title: "DIO Platform - Digital Immune Organism Security Dashboard",
    description: "Advanced cybersecurity platform powered by AI-driven Digital Immune Organism technology",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "DIO Platform - Digital Immune Organism Security Dashboard",
    description: "Advanced cybersecurity platform powered by AI-driven Digital Immune Organism technology",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
