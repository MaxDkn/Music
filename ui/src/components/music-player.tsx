import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Pause, Play, Volume2 } from "lucide-react"

type MusicPlayerProps = {
  src: string
  title: string
}

export default function MusicPlayer({ src, title }: MusicPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [volume, setVolume] = useState(0.5) // valeur de base 50%

  const togglePlay = () => {
    if (!audioRef.current) return
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateProgress = () => {
      setProgress((audio.currentTime / audio.duration) * 100 || 0)
    }

    audio.volume = volume

    audio.addEventListener("timeupdate", updateProgress)
    return () => {
      audio.removeEventListener("timeupdate", updateProgress)
    }
  }, [volume])

  const handleProgressChange = (value: number[]) => {
    if (audioRef.current && audioRef.current.duration) {
      audioRef.current.currentTime = (value[0] / 100) * audioRef.current.duration
      setProgress(value[0])
    }
  }

  const handleVolumeChange = (value: number[]) => {
    setVolume(value[0] / 100)
    if (audioRef.current) {
      audioRef.current.volume = value[0] / 100
    }
  }

  return (
    <div className="fixed bottom-0 left-0 w-full z-50 bg-background border-t shadow-md px-4 py-3 flex flex-col space-y-3">
      <audio ref={audioRef} src={src} preload="auto" />

      {/* Barre de progression pleine largeur */}
      <Slider
        value={[progress]}
        onValueChange={handleProgressChange}
        className="w-full"
      />

      <div className="flex items-center justify-between w-full flex-wrap gap-4">
        {/* Titre */}
        <div className="text-sm font-medium truncate">{title}</div>

        {/* Bouton play/pause */}
        <Button onClick={togglePlay} size="icon" variant="secondary">
          {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        </Button>

        {/* Volume */}
        <div className="flex items-center space-x-2 w-32">
          <Volume2 className="w-4 h-4" />
          <Slider
            value={[volume * 100]}
            onValueChange={handleVolumeChange}
            max={100}
            step={1}
          />
        </div>
      </div>
    </div>
  )
}
