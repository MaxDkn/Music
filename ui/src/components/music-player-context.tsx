"use client";

import {
  createContext,
  useContext,
  useRef,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { API_URL } from "@/data/api";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Pause, Play, Volume2 } from "lucide-react";
import Image from "next/image";


// Contexte pour le lecteur audio
interface MusicPlayerContextType {
  playTrack: (track: {
    id: string | number;
    title: string;
    author: string;
    coverImageUrl: string;
  }) => void;
  currentTrackId: string | null;
}

const MusicPlayerContext = createContext<
  MusicPlayerContextType | undefined
>(undefined);

interface MusicPlayerProviderProps {
  children: ReactNode;
}

export const MusicPlayerProvider = ({ children }: MusicPlayerProviderProps) => {
  const audioRef = useRef<HTMLAudioElement>(null);

  const [currentTrack, setCurrentTrack] = useState<{
    id: string;
    title: string;
    author: string;
    src: string;
    coverImageUrl: string;
  } | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0); // en pourcentage
  const [volume, setVolume] = useState(0.5);   // 0.0 → 1.0

  // Lance la lecture d'une piste
  const playTrack = (track: { id: string | number; title: string; author: string; coverImageUrl: string }) => {
    const idStr = track.id.toString();
    const src = `${API_URL}/audio?trackId=${idStr}`;

    setCurrentTrack({
      id: idStr,
      title: track.title,
      author: track.author,
      src,
      coverImageUrl: `${track.coverImageUrl}60x60.jpg`,
    });
    console.log(track.coverImageUrl);
    if (audioRef.current) {
      audioRef.current.src = src;
      const playPromise = audioRef.current.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => setIsPlaying(true))
          .catch((err) => console.warn("Impossible d’autoplay :", err));
      }
    }
  };

  // Met à jour le volume
  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  // Met à jour la progression
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      if (audio.duration) {
        setProgress((audio.currentTime / audio.duration) * 100);
      }
    };

    audio.addEventListener("loadedmetadata", updateProgress);
    audio.addEventListener("timeupdate", updateProgress);

    return () => {
      audio.removeEventListener("loadedmetadata", updateProgress);
      audio.removeEventListener("timeupdate", updateProgress);
    };
  }, [currentTrack]);

  // Play / Pause
  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      const playPromise = audioRef.current.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => setIsPlaying(true))
          .catch((err) => console.warn("Lecture interrompue :", err));
      }
    }
  };

  // Gère le changement de progression
  const handleProgressChange = (value: number[]) => {
    if (audioRef.current?.duration && value.length > 0) {
      const pct = value[0];
      audioRef.current.currentTime = (pct / 100) * audioRef.current.duration;
      setProgress(pct);
    }
  };

  // Gère le volume
  const handleVolumeChange = (value: number[]) => {
    if (value.length > 0) setVolume(value[0] / 100);
  };

  return (
    <MusicPlayerContext.Provider
      value={{ playTrack, currentTrackId: currentTrack?.id ?? null }}
    >
      {children}

      {/* Barre toujours visible */}
      <div className="fixed bottom-0 left-0 w-full z-50 bg-background border-t shadow-md px-4 py-3 flex items-center space-x-4">
        <audio ref={audioRef} preload="auto" />

        {/* Cover de l'album */}
        {currentTrack?.coverImageUrl && (
          <div className="hidden md:block flex-shrink-0 w-12 h-12 rounded-sm overflow-hidden">
            <Image
              src={currentTrack.coverImageUrl}
              alt={`${currentTrack.title} cover`}
              width={50}
              height={50}
              className="h-full w-full object-cover"
            />
          </div>
        )}

        {/* Infos piste */}
        <div className="flex-1 min-w-0">
          <p className="text-base font-semibold truncate">
            {currentTrack?.title || ""}
          </p>
          <p className="text-sm truncate text-muted-foreground">
            {currentTrack?.author || ""}
          </p>

          {/* Progression */}
          <Slider
            value={[progress]}
            onValueChange={handleProgressChange}
            max={100}
            step={0.1}
            className="w-full mt-2"
          />
        </div>

        {/* Contrôles */}
        <Button
          onClick={togglePlay}
          size="icon"
          variant="secondary"
          className=""  // ← Ajout de `mx-auto` pour centrer le bouton play/pause
        >
          {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        </Button>

        {/* Volume */}
        <div className="hidden md:block flex items-center space-x-2 space-y-2 w-32">
          <Volume2 className="w-4 h-4 mx-auto" />
          <Slider
            value={[volume * 100]}
            onValueChange={handleVolumeChange}
            max={100}
            step={1}
          />
        </div>
      </div>
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
