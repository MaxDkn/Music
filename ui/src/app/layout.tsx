import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import MusicPlayer from "@/components/music-player";
import { ThemeProvider } from "next-themes";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MusicApp",
  description: "Created by Max DECKMYN https://github.com/MaxDkn/music",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        {/* L'encapsulation par le ThemeProvider permet de gérer le thème pour toute l'application */}
        <ThemeProvider attribute="class" defaultTheme="system">
          <div className="min-h-screen flex flex-col">
            <main className="flex-grow pb-32">
              {children}
            </main>
            {/* Optionnel : Le MusicPlayer ou d'autres composants globaux */}
            {/* <MusicPlayer src="/audios/9bZkp7q19f0.mp3" title="Gagnam Style" /> */}
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
