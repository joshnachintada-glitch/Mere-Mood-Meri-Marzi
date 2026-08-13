// GradientBackground — "Silk Blend gradient", made with the 21st.dev Gradient
// Builder and exported as live CSS (the builder's own Copy-CSS background,
// plus its soften-blur and grain passes). Zero dependencies: one <div> that
// fills its parent. Drop it behind your content:
// <div className="relative h-96"><GradientBackground className="absolute inset-0" /></div>
// Remix the source recipe (colors, mode, finish) in the editor:
// https://21st.dev/community/gradients/editor?from=faef6ee1-8340-4ac1-930e-984262eea779
import { cn } from "@/lib/utils";

export function GradientBackground({ className }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={cn("relative w-full h-full overflow-hidden", className)}
      style={{
        containerType: "size",
      }}
    >
      <div
        style={{
          position: "absolute",
        inset: 0,
        backgroundColor: "#083DA9",
        backgroundImage:
          "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='0.080'/></svg>\"), linear-gradient(180deg, #083DA9 0%, #F7F3FF 51%, #02006F 100%, #000000 100%)",
        backgroundSize: "120px 120px, auto",
        backgroundBlendMode: "overlay, normal",
        }}
      />
      <svg
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          opacity: 0.080,
          mixBlendMode: "overlay",
        }}
      >
        <filter id="grain-faef6ee1">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.8"
            numOctaves="2"
            stitchTiles="stitch"
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain-faef6ee1)" />
      </svg>
    </div>
  )
}
