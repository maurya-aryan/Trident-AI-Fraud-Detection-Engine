import EmailFunnel from './trident-funnel/EmailFunnel';
import ParticleBackground from './ParticleBackground';

export default function DetectionSection() {
  return (
    <ParticleBackground>
      <section className="relative w-full bg-transparent z-10 overflow-hidden pt-20">
        <div className="relative z-10">
          <div className="text-center pt-20 pb-8 px-6">
            <p className="text-xs font-mono text-blue-400/60 uppercase tracking-[0.4em] mb-4">
              Real-Time Analysis
            </p>
            <h2 className="text-5xl md:text-6xl font-black tracking-tighter text-white uppercase italic mb-4">
              Email <span className="text-blue-400">Detection</span>
            </h2>
            <p className="text-blue-200/40 font-light text-lg max-w-2xl mx-auto leading-relaxed">
              Watch emails flow through the TRIDENT pipeline — each message is analyzed by 9 detection modules
              and classified as Fraud or Safe in real-time.
            </p>
          </div>

          <EmailFunnel />
        </div>
      </section>
    </ParticleBackground>
  );
}
