import InteractiveTerminal from './InteractiveTerminal';
import ConnectMailbox from './ConnectMailbox';

export default function TerminalSection() {
  return (
    <section className="relative min-h-[100vh] w-full flex flex-col items-center justify-center px-6 py-20 bg-background z-10">
      <div className="text-center mb-12">
        <h2 className="text-5xl font-black tracking-tighter text-white uppercase italic mb-4">
          Live <span className="text-blue-500">Detection</span>
        </h2>
        <p className="text-blue-200/60 font-mono text-sm max-w-2xl">
          Interact with the live TRIDENT engine. Execute analysis to see multi-modal signals processed in real-time.
        </p>
      </div>

      <div className="w-full max-w-4xl">
        <ConnectMailbox />
        <InteractiveTerminal />
      </div>
    </section>
  )
}
