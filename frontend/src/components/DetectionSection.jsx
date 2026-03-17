import EmailFunnel from './trident-funnel/EmailFunnel';
import ParticleBackground from './ParticleBackground';

export default function DetectionSection() {
  return (
    <ParticleBackground>
      <section className="relative w-full bg-transparent z-10 overflow-hidden py-20">
        <div className="relative z-10 max-w-[1200px] mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-12 md:gap-16">
          
          {/* LEFT COLUMN (45% split briefing panel) */}
          <div className="w-full md:w-[45%] flex flex-col justify-center text-center md:text-left">
            <p className="text-xs font-mono text-blue-400/60 uppercase tracking-[0.4em] mb-4">
              Real-Time Analysis
            </p>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tighter text-white uppercase italic mb-4">
              Email <span className="text-blue-400">Detection</span>
            </h2>
            <p className="text-blue-200/40 font-light text-base md:text-lg max-w-xl md:mx-0 mx-auto leading-relaxed mb-8">
              Watch emails flow through the TRIDENT pipeline — each message is analyzed by 9 detection modules
              and classified as Fraud or Safe in real-time.
            </p>

            {/* Stat Badges */}
            <div className="flex flex-wrap gap-3 mb-8 justify-center md:justify-start">
              <span className="inline-flex items-center px-4 py-1.5 rounded-full border border-blue-400/25 bg-blue-950/25 backdrop-blur-sm text-[10px] font-mono text-blue-300 tracking-wider">
                9 Detection Modules
              </span>
              <span className="inline-flex items-center px-4 py-1.5 rounded-full border border-blue-400/25 bg-blue-950/25 backdrop-blur-sm text-[10px] font-mono text-blue-300 tracking-wider">
                &lt;3ms Latency
              </span>
              <span className="inline-flex items-center px-4 py-1.5 rounded-full border border-blue-400/25 bg-blue-950/25 backdrop-blur-sm text-[10px] font-mono text-blue-300 tracking-wider">
                99.1% Accuracy
              </span>
            </div>

            {/* Bullet List */}
            <ul className="space-y-3 text-[12px] md:text-[13px] font-mono text-blue-100/50 flex flex-col items-center md:items-start tracking-wide">
              <li className="flex items-center gap-2">
                <span className="text-blue-400 text-sm">✦</span> Analyzes sender reputation
              </li>
              <li className="flex items-center gap-2">
                <span className="text-blue-400 text-sm">✦</span> Scans URL patterns & attachments
              </li>
              <li className="flex items-center gap-2">
                <span className="text-blue-400 text-sm">✦</span> Cross-references threat databases
              </li>
              <li className="flex items-center gap-2">
                <span className="text-blue-400 text-sm">✦</span> Outputs Fraud or Safe verdict
              </li>
            </ul>
          </div>

          {/* RIGHT COLUMN (55% split funnel area) */}
          <div className="w-full md:w-[55%] flex justify-center items-center">
            <div className="w-full flex justify-center md:justify-center">
              <EmailFunnel />
            </div>
          </div>

        </div>
      </section>
    </ParticleBackground>
  );
}
