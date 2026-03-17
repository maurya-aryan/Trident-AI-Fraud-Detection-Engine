export default function PipelineSection() {
  return (
    <section className="relative min-h-[120vh] w-full flex flex-col items-center justify-center px-6 py-20 bg-background z-10">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
          Adaptive threat modeling.
        </h2>
        <p className="text-lg text-white/60">
          Continuous model retraining. Graph-based relationship mapping. Real-time anomaly detection.
        </p>
      </div>

      <div className="w-full max-w-3xl aspect-[16/9] border border-white/10 rounded-3xl bg-surface/50 backdrop-blur-md flex items-center justify-center relative overflow-hidden">
        {/* Placeholder for Pipeline Visuals */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-accent/5 to-transparent"></div>
        <p className="text-white/40 font-mono tracking-widest text-sm z-10 uppercase">
          [ Detection Engine Pipeline Visual ]
        </p>
      </div>
    </section>
  )
}
