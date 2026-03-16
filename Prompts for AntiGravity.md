This setup is serious engineering. Combining a high-performance GSAP Canvas pipeline with Matter.js physics is exactly the kind of show-stopping architecture that would dominate a hackathon with Team Solaris. Moving from Framer Motion to GSAP ScrollTrigger for this specific use case is the absolute right call—it handles frame-scrubbing significantly better and gives you that buttery-smooth timeline control.

Here is the master prompt tailored precisely to your tech stack, scene breakdown, and layout requirements. You can copy and paste this directly to your AI agent.

The "Project Trident" Master Prompt
ACT AS:
A world-class Creative Developer (Awwwards-level) specializing in React 19, GSAP ScrollTrigger, HTML5 Canvas performance, and interactive physics.

THE TASK:
Build a high-end “Scrollytelling” pinned Hero Section for a project called “Project Trident”.
The core mechanic is a massive pinned section where user scrolling scrubs through a high-resolution 192-frame image sequence drawn on an HTML5 <canvas>. As the sequence progresses, different placeholder text overlays fade in and out. In the final scene, a Matter.js physics simulation is triggered over the canvas. Once the 192 frames finish, the hero section unpins, and the user can scroll normally to the rest of the website.

TECH STACK:

Framework: React 19 + Vite (Node.js)

Styling: Tailwind CSS + Vanilla CSS (for custom glassmorphism / ethereal UI glows)

Animation Engine: GSAP (ScrollTrigger for timeline mapping and pinning)

Physics Engine: Matter.js (2D physics for Scene 3)

Rendering: HTML5 Canvas (to render 1920x1080 frames without DOM lag)

VISUAL DIRECTION (Deep Ocean Cinematic Theme):

Background: The canvas backdrop must be a deep, dark oceanic navy/black (e.g., #040914 to #000000) to seamlessly blend the edges of the frames.

UI Aesthetic: High-tech, mysterious, premium glassmorphism. Text overlays should feel like classified HUD elements or sleek editorial typography.

Responsiveness: The canvas must use a cover or contain calculation algorithm on resize so the trident is always centered and visible across all devices.

IMPLEMENTATION DETAILS & SCENE MAPPING:

1) The Pinned Hero Architecture

Create a component TridentHero.jsx.

Set up a massive scrolling container (e.g., h-[400vh]).

Use GSAP ScrollTrigger to pin the canvas and text overlay container to the viewport while the user scrolls through the 400vh space.

Below this hero component, create a standard div (e.g., <section className="h-screen bg-black text-white">Other Website Content</section>) to prove the unpinning works.

2) Canvas Sequence Player (GSAP + Canvas)

Load a sequence of 192 images (Frames 1 to 192). Assume a naming convention like /frames/trident_%03d.webp.

Implement a robust preloader. Show a sleek, glowing loading state until a critical mass of frames is cached.

Map the GSAP ScrollTrigger progress (0 to 1) directly to the frame index. Draw using requestAnimationFrame to ensure zero jank. Avoid redundant repaints.

3) The Story Beats (Placeholder Overlays)
Sync these UI overlays to the GSAP timeline progress:

Scene 1: The Surface (Frames 1–60) * Visuals: Sunrays piercing the water.

UI: Center-aligned glassmorphism card. [PLACEHOLDER TITLE 1] / [PLACEHOLDER SUBTEXT 1].

Scene 2: The Descent (Frames 61–120)

Visuals: The Trident dropping through the water.

UI: Left or right-aligned sleek text revealing the project context. [PLACEHOLDER TITLE 2] / [PLACEHOLDER SUBTEXT 2].

Scene 3: The Abyss & The Funnel (Frames 121–192)

Visuals: The Trident rests in the dark abyss.

UI: [PLACEHOLDER FINAL CTA].

INTERACTION: At this exact scroll threshold, initialize/unpause a Matter.js simulation over the canvas. "Intercepted emails" (represented as small glassmorphic rectangles or icons) should drop from the top of the screen and bounce into a physics-based visual funnel at the bottom of the viewport.

4) Performance & Polish Requirements:

Handle devicePixelRatio for sharp canvas rendering on retina screens.

Kill and rebuild GSAP ScrollTriggers gracefully on window resize.

Ensure the Matter.js <canvas> or DOM elements sit cleanly on a higher z-index than the video frame <canvas>, with pointer events correctly managed.

OUTPUT:
Generate the React 19 code for TridentHero.jsx (including the GSAP mapping, Canvas rendering, and Matter.js integration) and any necessary CSS/utility files. Ensure the code is modular, heavily commented, and ready to drop into a Vite environment.