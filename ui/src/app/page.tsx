"use client"

import { useEffect, useState } from "react"
import { PlusCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { API_URL } from "@/data/api"
import Link from "next/link"
import Image from "next/image"
import { cn } from "@/lib/utils"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { AlbumArtwork } from "@/components/album-artwork"

interface Track {
  trackId: number
  trackName: string
  artistName: string
  coverImageUrl: string
}

export default function MusicPage() {
  const [largeTracks, setLargeTracks] = useState<Track[]>([])
  const [smallTracks, setSmallTracks] = useState<Track[]>([])
  const [empty, setEmpty] = useState(false);

  useEffect(() => {
    async function fetchTracks() {
      try {
        const res4 = await fetch(`${API_URL}/foryou?limit=6 `)
        const json4 = await res4.json()
        setLargeTracks(json4)

        const res5 = await fetch(`${API_URL}/foryou?limit=5`)
        const json5 = await res5.json()
        setSmallTracks(json5)
        if (largeTracks.length === 0 && smallTracks.length === 0) {
          setEmpty(true)
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des pistes:", error)
      }
    }
    fetchTracks()
  }, [])
 
  return (
    <div className="h-full px-4 py-6 md:px-8">
      <Tabs defaultValue="music" className="h-full space-y-6">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="music" className="relative">
              Music
            </TabsTrigger>
            <TabsTrigger value="podcasts" disabled>
              Podcasts
            </TabsTrigger>
          </TabsList>
          <div className="ml-auto mr-4">
            <Button>
              <PlusCircle /> Add music
            </Button>
          </div>
        </div>

        <TabsContent value="music" className="border-none p-0 outline-none">
          {/* Grandes pistes */}
          <div className="space-y-1">
            {(!empty) ? (
              <div>
              <h2 className="text-2xl font-semibold tracking-tight">
                Listen Now
              </h2>
              <p className="text-sm text-muted-foreground">
                Based on your recent listening activity
              </p>
              </div>
            ) : (
              <div>
              <h2 className="text-2xl font-semibold tracking-tight">
                Hi Music !
              </h2>
              <p className="text-sm text-muted-foreground">
              Discover and enjoy your favorite tracks. Head over to the <Link href="/browse"><strong>Browse</strong></Link> tab to upload and explore music.
              </p>
              </div>
            )}
          </div>
          <Separator className="my-4" />
          { (empty) ? (
          <div>
          <div className="relative">
            <ScrollArea>
              <div className="flex space-x-4 pb-4">
                {largeTracks.map((track) => (
                  <AlbumArtwork
                    key={track.trackId}
                    album={{
                      name: track.trackName,
                      artist: track.artistName,
                      coverImageUrl: `${track.coverImageUrl}1000x1000.jpg`,
                    }}
                    className="w-[250px]"
                    aspectRatio="square"
                    width={330}
                    height={330}
                  />
                ))}
              </div>
              <ScrollBar orientation="horizontal" />
            </ScrollArea>
          </div>

          {/* Petites pistes */}
          <div className="mt-6 space-y-1">
            <h2 className="text-2xl font-semibold tracking-tight">
              More For You
            </h2>
          </div>
          <Separator className="my-4" />
          <div className="relative">
            <ScrollArea>
              <div className="flex space-x-4 pb-4">
                {smallTracks.map((track) => (
                  <AlbumArtwork
                    key={track.trackId}
                    album={{
                      name: track.trackName,
                      artist: track.artistName,
                      coverImageUrl: `${track.coverImageUrl}300x300.jpg`,
                    }}
                    className="w-[150px]"
                    aspectRatio="square"
                    width={150}
                    height={150}
                  />
                ))}
              </div>
              <ScrollBar orientation="horizontal" />
            </ScrollArea>
          </div>
          </div>
          ) : (
            <div className="flex items-center justify-center space-x-6 border border-muted-foreground rounded-md">
              <div className="flex-shrink-0">
              <Image
                src="/hi.png"
                alt="Music Placeholder"
                width={450}
                height={450}
                className={cn(
                "object-cover transition-all hover:scale-105 rounded-md"
                )}
              />
              </div>
              <div className="flex-grow text-center">
              <h2 className="text-2xl font-semibold tracking-tight">
                Here your music will be!
              </h2>
              </div>
            </div>
          )}
          {/*aspectRatio === "portrait" ? "aspect-[3/4]" : "aspect-square"*/}
        </TabsContent>
      </Tabs>
    </div>
  )
}
