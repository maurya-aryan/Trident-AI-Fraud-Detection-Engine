import { useRef, useState, useEffect } from 'react';
import InteractiveTerminal from './InteractiveTerminal';
import ParticleBackground from './ParticleBackground';

export default function TerminalSection() {
  return (
    <div className="relative z-20 rounded-t-[24px] shadow-[0_-20px_60px_rgba(0,0,0,0.8)] mt-[-45vh] bg-[#050b18] pt-[80px]">
      <ParticleBackground>
        <section className="relative w-full flex flex-col items-center justify-center px-6 bg-transparent z-10">
          <InteractiveTerminal />
        </section>
      </ParticleBackground>
    </div>
  );
}
