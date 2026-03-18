# TRIDENT Component Refactoring Guide

This guide documents the recommended approach for splitting large frontend components.

## Overview

Three large components need refactoring:
- **EmailFunnel.jsx** (699 lines)
- **InteractiveTerminal.jsx** (431 lines)
- **HeroSection.jsx** (417 lines)

All have been partially prepared with:
- ✅ Centralized API calls in `src/lib/api.js`
- ✅ Constants extracted to `src/constants/index.js`
- ✅ Custom hooks available in `src/hooks/`
- ✅ Directory structure created for split components

---

## 1. EmailFunnel.jsx Refactoring

**Current:** 699 lines - Monolithic funnel with embedded animations and stage logic

**Target Structure:**
```
src/components/funnel/
├── EmailFunnel.jsx           # Orchestrator (~150 lines)
├── FunnelStage.jsx            # Individual stage component
├── FunnelAnimations.js        # GSAP timeline logic
└── funnelConfig.js           # Stage definitions
```

### Steps:

#### A. Extract Animation Logic

Create `funnel/FunnelAnimations.js`:
```javascript
import gsap from 'gsap';

export function animateStageIn(element, delay = 0) {
  return gsap.from(element, {
    opacity: 0,
    y: 50,
    duration: 0.6,
    delay,
  });
}

export function animateStageOut(element) {
  return gsap.to(element, {
    opacity: 0,
    y: -50,
    duration: 0.4,
  });
}

export function createFunnelTimeline(stages) {
  const tl = gsap.timeline();
  stages.forEach((stage, index) => {
    tl.add(animateStageIn(stage, index * 0.2));
  });
  return tl;
}
```

#### B. Extract Stage Component

Create `funnel/Funnel Stage.jsx`:
```javascript
export function FunnelStage({ stage, active, result, onComplete }) {
  return (
    <div className={`funnel-stage ${active ? 'active' : ''}`}>
      <h3>{stage.title}</h3>
      <div className="stage-content">
        {stage.render(result)}
      </div>
      {result && <StageResult data={result} />}
    </div>
  );
}
```

#### C. Refactor Main Component

`funnel/EmailFunnel.jsx` becomes orchestrator:
```javascript
import { useFunnel } from '../../hooks';
import { FunnelStage } from './FunnelStage';
import { animateStageIn } from './FunnelAnimations';
import { FUNNEL_STAGES } from './funnelConfig';

export function EmailFunnel() {
  const { currentStage, results, advance } = useFunnel(FUNNEL_STAGES);

  return (
    <div className="email-funnel">
      {FUNNEL_STAGES.map((stage, index) => (
        <FunnelStage
          key={stage.id}
          stage={stage}
          active={index === currentStage}
          result={results[stage.id]}
          onComplete={advance}
        />
      ))}
    </div>
  );
}
```

---

## 2. InteractiveTerminal.jsx Refactoring

**Current:** 431 lines - Terminal with embedded SSE, API calls, and rendering

**Target Structure:**
```
src/components/terminal/
├── InteractiveTerminal.jsx    # Main component (~150 lines)
├── TerminalOutput.jsx          # Pure output rendering
├── TerminalControls.jsx        # Start/Stop buttons
└── useTerminalStream.js       # Custom hook for SSE
```

### Steps:

#### A. Already Done ✅
- API calls centralized in `src/lib/api.js`
- API_URL imported from constants

#### B. Extract Output Rendering

Create `terminal/TerminalOutput.jsx`:
```javascript
export function TerminalOutput({ lines }) {
  return (
    <div className="terminal-output">
      {lines.map((line, index) => (
        <TerminalLine key={index} line={line} />
      ))}
    </div>
  );
}

function TerminalLine({ line }) {
  const className = `term-line term-${line.type}`;
  return <div className={className}>{line.text}</div>;
}
```

#### C. Use Existing Hooks

```javascript
import { usePollerStream } from '../../hooks';

export function InteractiveTerminal() {
  const { logs, status, connected } = usePollerStream();

  return (
    <div className="terminal">
      <TerminalOutput lines={logs} />
      <StatusBar connected={connected} status={status} />
    </div>
  );
}
```

---

## 3. HeroSection.jsx Refactoring

**Current:** 417 lines - 3D scene + text + scroll animations

**Target Structure:**
```
src/components/hero/
├── HeroSection.jsx            # Layout shell (~100 lines)
├── TridentModel.jsx           # 3D model logic
├── HeroText.jsx               # Text content
└── useScrollAnimation.js     # Scroll-driven GSAP
```

### Steps:

#### A. Extract 3D Model

Create `hero/TridentModel.jsx`:
```javascript
import { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

export function TridentModel({ modelPath }) {
  const containerRef = useRef();

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true });

    const loader = new GLTFLoader();
    loader.load(modelPath, (gltf) => {
      scene.add(gltf.scene);
    });

    // Animation loop...
    return () => renderer.dispose();
  }, [modelPath]);

  return <div ref={containerRef} className="trident-model" />;
}
```

#### B. Extract Scroll Hook

Create `hero/useScrollAnimation.js`:
```javascript
import { useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

export function useScrollAnimation(targetRef) {
  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: targetRef.current,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    });

    tl.to(targetRef.current, { opacity: 0, y: -100 });

    return () => tl.kill();
  }, [targetRef]);
}
```

---

## Benefits of This Refactoring

1. **Maintainability**: Each file has single responsibility
2. **Reusability**: Extracted components/hooks can be used elsewhere
3. **Testing**: Smaller units are easier to test
4. **Performance**: Easier to optimize individual pieces
5. **Collaboration**: Multiple devs can work on different parts

---

## Implementation Priority

1. **High Priority** - InteractiveTerminal (already uses new hooks)
2. **Medium Priority** - EmailFunnel (complex but high-value)
3. **Low Priority** - HeroSection (mostly visual, less business logic)

---

## Testing Strategy

After each refactor:
```bash
# Frontend tests
cd frontend
npm run dev        # Visual check
npm run build      # Ensure no build errors
npm run lint       # Check code quality

# Backend still works
cd ../backend
python -m pytest   # Run backend tests
```

---

## Notes

- **DO NOT** refactor all at once - do incrementally
- **ALWAYS** test after each file extraction
- **PRESERVE** all existing CSS classes and IDs
- **MAINTAIN** backward compatibility with existing props
- **USE** the new hooks and API client from Steps 9-10
