export default function TerminalSection() {
  return (
    <section className="relative min-h-[100vh] w-full flex flex-col items-center justify-center px-6 py-20 bg-background z-10">
      <div className="w-full max-w-4xl bg-[#0c0e14] border border-accent/20 rounded-xl overflow-hidden shadow-[0_0_60px_rgba(0,214,255,0.05)]">
        {/* Terminal Header */}
        <div className="flex items-center gap-2 px-4 py-3 bg-white/5 border-b border-white/5">
          <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
          <span className="ml-4 text-xs font-mono text-white/40">trident-core@engine: ~</span>
        </div>
        
        {/* Terminal Body */}
        <div className="p-6 font-mono text-sm leading-relaxed h-[400px] overflow-y-auto">
          <div className="text-white/60 mb-2">
            <span className="text-green-400 mr-2">[INFO]</span> 
            System initialized. Awaiting data stream...
          </div>
          <div className="text-white/60 mb-2">
            <span className="text-accent mr-2">[STREAM]</span> 
            Connected to global transaction ledger.
          </div>
          <div className="text-white/60 mb-2">
            <span className="text-yellow-400 mr-2">[WARN]</span> 
            Anomaly detected in Node 7X-Cluster.
          </div>
          <div className="text-white/60 mb-2">
            <span className="text-red-400 mr-2 font-bold">[BLOCKED]</span> 
            Transaction ID #88492 intercepted. Fraud probability 99.8%.
          </div>
          
          <div className="mt-6 flex items-center text-white/80">
            <span className="text-accent mr-2">root@trident:~$</span>
            <span className="w-2 h-4 bg-white/80 animate-pulse inline-block align-middle"></span>
          </div>
        </div>
      </div>
    </section>
  )
}
