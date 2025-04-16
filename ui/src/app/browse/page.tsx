"use client";

import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

const API_URL = process.env.API_URL || "http://localhost/api";
const DELAY = 500;

interface ITunesTrack {
  trackId: number;
  trackName: string;
  artistName: string;
  artworkUrl: string;
  statusCode: number;
}

const searchITunes = async (query: string): Promise<ITunesTrack[]> => {
  const res = await fetch(`${API_URL}/music/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Erreur lors de la recherche");
  }
  return res.json();
};

export default function BrowsePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  // État pour stocker un éventuel nouveau statusCode après téléchargement
  const [downloadStatus, setDownloadStatus] = useState<Record<number, number>>({});
  const pollingRefs = useRef<Record<
    number,
    { timeoutId?: NodeJS.Timeout; intervalId?: NodeJS.Timeout }
  >>({});

  useEffect(() => {
    const handler = setTimeout(() => {
      if (
        searchTerm.endsWith(" ") &&
        searchTerm.trim() === debouncedSearchTerm.trim()
      ) {
        return;
      }
      setDebouncedSearchTerm(searchTerm);
    }, DELAY);
  
    return () => clearTimeout(handler);
  }, [searchTerm, debouncedSearchTerm]);
  

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["itunes", debouncedSearchTerm],
    queryFn: () => searchITunes(debouncedSearchTerm),
    enabled: !!debouncedSearchTerm,
    staleTime: 5 * 60 * 1000,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
  });

  const pollTrack = async (trackId: number) => {
    try {
      const res = await fetch(`${API_URL}/music/download?trackId=${trackId}`);
      const { statusCode, nextRun } = await res.json();
      setDownloadStatus((prev) => ({ ...prev, [trackId]: statusCode }));

      // Si ce n'est *toujours* pas prêt, on reste en polling
      if (statusCode !== 200) {
        // Rien à faire ici : l'intervale continuera d'appeler pollTrack
        return;
      }

      // Dès qu'on atteint 200, on stoppe tous les timers pour ce track
      const { timeoutId, intervalId } = pollingRefs.current[trackId] || {};
      timeoutId && clearTimeout(timeoutId);
      intervalId && clearInterval(intervalId);
      delete pollingRefs.current[trackId];
    } catch {
      // Vous pouvez gérer les erreurs réseau ici
    }
  };

  const handleTrackClick = async (trackId: number) => {
    // Cancel timers existants (sécurité si on reclique rapidement)
    const existing = pollingRefs.current[trackId];
    if (existing) {
      existing.timeoutId && clearTimeout(existing.timeoutId);
      existing.intervalId && clearInterval(existing.intervalId);
    }

    // Premier appel
    try {
      const res = await fetch(`${API_URL}/music/download?trackId=${trackId}`);
      const { statusCode, nextRun } = await res.json();
      setDownloadStatus((prev) => ({ ...prev, [trackId]: statusCode }));

      // Si déjà prêt, on ne fait rien d'autre
      if (statusCode === 200) {
        return;
      }

      // 5) Si pas prêt : attendre nextRun+1 sec, puis un appel, puis polling 8s
      const timeoutId = setTimeout(() => {
        // Un premier retry
        pollTrack(trackId);
        // Ensuite on bascule en mode interval
        const intervalId = setInterval(() => pollTrack(trackId), 15_000);
        pollingRefs.current[trackId].intervalId = intervalId;
      }, (nextRun + 1) * 1_000);

      // On stocke notre timeout
      pollingRefs.current[trackId] = { timeoutId };
    } catch (err) {
      console.error(err);
    }
  };
  
  return (
    <div className="p-4">
      <form onSubmit={(e) => e.preventDefault()} className="flex justify-center mb-8">
        <div className="relative w-xl">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            autoFocus
            placeholder="Search"
            className="pl-10 h-12 text-lg"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </form>
      {isLoading && (
        <div className="grid gap-4">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              <Skeleton className="w-12 h-12 rounded" />
              <div className="flex flex-col gap-1">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
          ))}
        </div>
      )}
      {isError && <p className="text-red-500">{(error as Error).message}</p>}
      {!isLoading && data && (
        <div className="grid gap-4">
          {data.map((track: ITunesTrack) => {
            // Utiliser le statusCode mis à jour s'il existe, sinon celui d'origine
            const statusCode = downloadStatus[track.trackId] ?? track.statusCode;
            
            return (
              <div
                key={track.trackId}
                onClick={() => handleTrackClick(track.trackId)}
                className="group relative flex items-center gap-4 p-2 border rounded hover:shadow-lg transition-shadow cursor-pointer"
              >
                
                  <img
                    src={`${track.artworkUrl}60x60bb.jpg`}
                    alt={track.trackName}
                    className="w-12 h-12 rounded"
                  />
                  <div className="absolute inset-0 rounded bg-black opacity-0 group-hover:opacity-5 transition-opacity"></div>
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    {statusCode === 100 && (
                      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
                        <path d="m11.966 11.136-.004 8M19.825 17c4.495-3.16.475-7.73-3.706-7.73C13.296-1.732-3.265 7.368 4.074 15.662m11.07 1.156L11.962 20 8.78 16.818"/>
                      </svg>
                    )}
                    {statusCode === 200 && (
                      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14.581 9.402C16.194 10.718 17 11.375 17 12.5s-.806 1.783-2.419 3.098a23 23 0 0 1-1.292.99c-.356.25-.759.508-1.176.762-1.609.978-2.413 1.467-3.134.926-.722-.542-.787-1.675-.918-3.943A33 33 0 0 1 8 12.5c0-.563.023-1.192.06-1.833.132-2.267.197-3.401.919-3.943.721-.541 1.525-.052 3.134.926.417.254.82.512 1.176.762a23 23 0 0 1 1.292.99"/>
                      </svg>
                    )}
                    {statusCode === 101 && (
                      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                        <path d='M12 3v3m6.366-.366-2.12 2.12M21 12h-3m.366 6.366-2.12-2.12M12 21v-3m-6.366.366 2.12-2.12M3 12h3m-.366-6.366 2.12 2.12'/>
                      </svg>
                    )}
                    {statusCode === 102 && (
                      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 3v3m0 15v-3m-7.794-1.5L6.804 15M21 12h-3m-1.5 7.794L15 17.196M3 12h3m1.5-7.794L9 6.804m-1.5 12.99L9 17.196m10.794-.696L17.196 15M4.206 7.5 6.804 9"/>
                      </svg>
                    )}
                    
                    
                    {! [100,101,102,200].includes(statusCode) && (
                      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0" />
                        <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0m-3-6L6 18" />
                      </svg>
                    )}
                  </div>
                
                <div className="flex flex-col">
                  <p className="font-medium">{track.trackName}</p>
                  <p className="text-sm text-muted-foreground">{track.artistName}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
