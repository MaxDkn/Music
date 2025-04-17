"use client";


import { createContext, useContext, useRef, useState, ReactNode } from "react";
import { API_URL } from "@/data/api";

interface MusicPlayerContextType {
  playTrack: (trackId: string | number) => void;
  currentTrackId: string | null;
}

const MusicPlayerContext = createContext<MusicPlayerContextType | undefined>(undefined);

interface MusicPlayerProviderProps {
  children: ReactNode;
}

export const MusicPlayerProvider = ({ children }: MusicPlayerProviderProps) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [currentTrackId, setCurrentTrackId] = useState<string | null>(null);

  const playTrack = (trackId: string | number) => {
      const id = typeof trackId === 'number' ? trackId.toString() : trackId;
      setCurrentTrackId(id);
      if (audioRef.current) {
        audioRef.current.src = `${API_URL}/audio?trackId=${id}`;
        audioRef.current.play();
    }
  };

  return (
    <MusicPlayerContext.Provider value={{ playTrack, currentTrackId }}>
      {children}
      <audio ref={audioRef} controls style={{ position: "fixed", bottom: 0 }} />
    </MusicPlayerContext.Provider>
  );
};

export const useMusicPlayer = () => {
  const context = useContext(MusicPlayerContext);
  if (!context) {
    throw new Error("useMusicPlayer must be used within a MusicPlayerProvider");
  }
  return context;
};
