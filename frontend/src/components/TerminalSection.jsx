import InteractiveTerminal from './InteractiveTerminal';

export default function TerminalSection() {
  return (
    <section className="relative min-h-[100vh] w-full flex flex-col items-center justify-center px-6 py-20 bg-background z-10">
      <div className="w-full max-w-4xl">
        <InteractiveTerminal />
      </div>
    </section>
  )
}
