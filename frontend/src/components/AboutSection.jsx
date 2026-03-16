export default function AboutSection() {
  const features = [
    { title: "Real-time Processing", desc: "Sub-millisecond latency on every transaction." },
    { title: "Graph Neural Networks", desc: "Maps deeply connected fraud rings instantly." },
    { title: "Adaptive Defense", desc: "Self-healing models that learn from new attack vectors." },
    { title: "Deterministic Actions", desc: "Zero false-positive enforcement policies." },
  ];

  return (
    <section className="relative min-h-screen w-full flex flex-col justify-center px-6 py-20 bg-background z-10">
      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <div className="space-y-6">
          <h2 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Precision-engineered intelligence.
          </h2>
          <p className="text-lg text-white/60 leading-relaxed max-w-lg">
            Multi-layered neural networks analyze thousands of features in milliseconds. Every transaction, vetted in real-time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature, idx) => (
            <div 
              key={idx} 
              className="glass-panel p-6 rounded-2xl hover:border-accent/40 transition-colors duration-300"
            >
              <h3 className="text-xl font-semibold text-white/90 mb-2">{feature.title}</h3>
              <p className="text-sm text-white/50">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
