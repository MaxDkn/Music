import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
{/* import MusicPlayer from "@/components/music-player"; */}
import { Menu } from "@/components/menu"
import "./globals.css";
import { Sidebar } from "@/components/sidebar"
import { playlists } from "@/data/playlists"
import { ThemeProvider } from "next-themes";
import { Providers } from "@/components/providers";

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
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <Providers>
        {/* L'encapsulation par le ThemeProvider permet de gérer le thème pour toute l'application */}
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="min-h-screen flex flex-col">
            <main className="flex-grow pb-32">
              <Menu/>
              <div className="grid grid-cols-1 md:grid-cols-5 bg-background border-t">
                <Sidebar playlists={playlists} className="hidden md:block" />
                <div className="col-span-1 md:col-span-4 border-l md:border-l">
                  {children}
                </div>              
              </div>
            </main>
            {/* Optionnel : Le MusicPlayer ou d'autres composants globaux */}
            {/* <MusicPlayer src="/audios/9bZkp7q19f0.mp3" title="Gagnam Style" /> */}
          </div>
        </ThemeProvider>
        </Providers>        
      </body>
    </html>
  );
}
