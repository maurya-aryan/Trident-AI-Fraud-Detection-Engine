import InteractiveTerminal from './InteractiveTerminal';
import Particles from './Particles';

export default function TerminalSection() {
  return (
    <section className="relative min-h-[100vh] w-full flex flex-col items-center justify-center px-6 py-20 bg-background z-10 overflow-hidden">
      {/* Particles Background Effect */}
      <div className="absolute inset-0 z-0">
        <Particles
          particleCount={200}
          particleSpread={10}
          speed={0.1}
          particleColors={["#ffffff", "#ffffff", "#ffffff"]}
          moveParticlesOnHover={false}
          particleHoverFactor={1}
          alphaParticles={false}
          particleBaseSize={100}
          sizeRandomness={1}
          cameraDistance={20}
          disableRotation={false}
        />
      </div>

      <div className="relative text-center mb-12 z-10">
        <h2 className="text-5xl font-black tracking-tighter text-white uppercase italic mb-4">
          Live <span className="text-blue-500">Detection</span>
        </h2>
        <p className="text-blue-200/60 font-mono text-sm max-w-2xl">
          Interact with the live TRIDENT engine. Execute analysis to see multi-modal signals processed in real-time.
        </p>
      </div>

      <InteractiveTerminal />
    </section>
  )
}
