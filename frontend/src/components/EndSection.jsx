export default function EndSection() {
  return (
    <section className="relative min-h-[60vh] w-full flex flex-col items-center justify-center px-6 py-20 bg-background z-10 border-t border-accent/10">
      <div className="absolute inset-0 bg-gradient-to-t from-accent/5 to-transparent pointer-events-none"></div>
      
      <div className="z-10 text-center max-w-2xl">
        <h2 className="text-4xl md:text-5xl font-black mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
          Secure your entire ecosystem.
        </h2>
        <p className="text-lg text-white/60 mb-10">
          Trident AI. Built for scale, forged for protection.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button className="px-8 py-3 rounded-full bg-accent text-background font-bold hover:bg-white transition-colors duration-300 shadow-[0_0_20px_rgba(0,214,255,0.3)]">
            Initialize Trident
          </button>
          <button className="px-8 py-3 rounded-full bg-transparent border border-white/20 text-white/80 font-medium hover:border-white/50 hover:text-white transition-colors duration-300">
            View Engine Specs
          </button>
        </div>
      </div>
      
      <footer className="absolute bottom-6 w-full text-center text-xs text-white/30 font-mono">
        <p>System Online. Copyright © 2026 TRIDENT AI Engine.</p>
      </footer>
    </section>
  )
}
