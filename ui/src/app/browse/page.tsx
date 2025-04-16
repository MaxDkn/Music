"use client";

import { useState, useEffect } from "react";
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
  if (!res.ok) throw new Error("Erreur lors de la recherche");
  return res.json();
};

export default function BrowsePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, DELAY);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["itunes", debouncedSearchTerm],
    queryFn: () => searchITunes(debouncedSearchTerm),
    enabled: !!debouncedSearchTerm,
    staleTime: 5 * 60 * 1000,
  });

  return (
    <div className="p-4">
      {/* Barre de recherche centrée */}
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

      {/* Templates de chargement */}
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

      {isError && <p className="text-red-500">Erreur lors du chargement des données.</p>}

      {!isLoading && data && data.length === 0 && (
        <p className="text-muted-foreground">Aucun résultat trouvé.</p>
      )}

      {/* Affichage des résultats */}
      {!isLoading && data && data.length > 0 && (
        <div className="grid gap-4">
          {data.map((track: ITunesTrack) => (
            <a
              key={track.trackId}
              href={`/track/${track.trackId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="group relative flex items-center gap-4 p-2 border rounded hover:shadow-lg transition-shadow"
            >
              <div className="relative">
                <img
                  src={`${track.artworkUrl}60x60bb.jpg`}
                  alt={track.trackName}
                  className="w-12 h-12 rounded"
                />
                <div className="absolute inset-0 rounded bg-black opacity-0 group-hover:opacity-20 transition-opacity"></div>
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  {track.statusCode === 100 && (
                    <svg
                      width="24"
                      height="24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      viewBox="0 0 24 24"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="m11.966 11.136-.004 8M19.825 17c4.495-3.16.475-7.73-3.706-7.73C13.296-1.732-3.265 7.368 4.074 15.662m11.07 1.156L11.962 20 8.78 16.818"/>
                    </svg>
                  )}
                  {track.statusCode === 200 && (
                    <svg
                      width="24"
                      height="24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      viewBox="0 0 24 24"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M14.581 9.402C16.194 10.718 17 11.375 17 12.5s-.806 1.783-2.419 3.098a23 23 0 0 1-1.292.99c-.356.25-.759.508-1.176.762-1.609.978-2.413 1.467-3.134.926-.722-.542-.787-1.675-.918-3.943A33 33 0 0 1 8 12.5c0-.563.023-1.192.06-1.833.132-2.267.197-3.401.919-3.943.721-.541 1.525-.052 3.134.926.417.254.82.512 1.176.762a23 23 0 0 1 1.292.99"/>
                    </svg>
                  )}
                  {/* Aucun icône pour les autres statusCode */}
                </div>
              </div>
              <div className="flex flex-col">
                <p className="font-medium">{track.trackName}</p>
                <p className="text-sm text-muted-foreground">{track.artistName}</p>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
