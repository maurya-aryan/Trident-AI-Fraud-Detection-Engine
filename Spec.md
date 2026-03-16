# **TRIDENT\_FRONTEND\_SPEC.md**

**Project:** TRIDENT Email Threat Detection System

**Architecture:** Video-to-Frames Scrubbing \+ Hybrid 2D Physics

## ---

**1\. Project Overview & Architecture Tree**

**TRIDENT** is a cinematic, highly interactive landing page designed to visualize a sophisticated cybersecurity backend. The architecture bypasses heavy 3D WebGL rendering in favor of a hybrid approach: scrubbing pre-rendered AI video frames (at 15fps) synced to the user's scroll, combined with a real-time 2D physics engine (Matter.js) overlaying static high-fidelity AI imagery.

## **Directory Structure**

Plaintext

src/  
├── App.jsx                        \# Main orchestrator & GSAP ScrollTrigger context  
├── components/  
│   ├── SequencePlayer.jsx         \# Handles Canvas drawing & frame preloading  
│   ├── FeatureRow.jsx             \# Scene 2: Tech stack feature items  
│   ├── PhysicsPipeline.jsx        \# Scene 3: Matter.js engine & Y-funnel overlay  
│   ├── InboxOverlay.jsx           \# Scene 4: Glassmorphism nested UI  
│   ├── ThreatInspector.jsx        \# Scene 4: Deep dive email view & SHAP chart  
│   └── InteractiveTerminal.jsx    \# Scene 5: Executable Python logs  
├── data/  
│   ├── features.json              \# Data for Scene 2  
│   ├── mockEmails.js              \# Intercepted payload data  
│   └── terminalLogs.js            \# Typewriter strings for Scene 5  
├── hooks/  
│   ├── useFrameLoader.js          \# Logic for fetching/caching sequence JPEGs  
│   └── useScrollLock.js           \# Utility to freeze body scroll during Scene 4  
└── styles/  
    └── index.css                  \# Tailwind directives & custom CSS animations  
public/  
├── sequences/  
│   ├── hero-rise/                 \# Video 1: 0001.jpg \- 0045.jpg  
│   ├── hero-right/                \# Video 2: 0001.jpg \- 0075.jpg  
│   └── hero-hover/                \# Video 3: 0001.jpg \- 0060.jpg  
└── images/  
    └── y-funnel-base.jpg          \# Image 1: Static background for Scene 3

## ---

**2\. Global Rules**

* **Canvas Setup:** The primary sequence \<canvas\> must be position: fixed, top: 0, left: 0, covering 100vw and 100vh. Set object-fit: cover logic inside the drawing function to handle aspect ratios.  
* **Z-Indexing Strategy:**  
  * z-index: 0 — Primary Video Frame \<canvas\>  
  * z-index: 10 — Physics Pipeline Background & Matter.js \<canvas\>  
  * z-index: 20 — Standard HTML UI (Taglines, Features, Terminals)  
  * z-index: 50 — Inbox Overlay (Scene 4\)  
* **15fps Frame Extraction Logic:**  
  * AI-generated MP4s must be converted to JPEGs at exactly 15 frames per second to balance smooth scrubbing with memory payload.  
  * *Extraction Command Example:* ffmpeg \-i input.mp4 \-vf fps=15 public/sequences/hero-rise/%04d.jpg  
* **Preloading:** The SequencePlayer.jsx must preload the next scene's frames into a hidden JS Image() array before the user reaches the scroll trigger to prevent flickering.

## ---

**3\. Scene-by-Scene Breakdown**

## **Scene 1: The Awakening (Hero Entry)**

* **Trigger:** DOMContentLoaded  
* **Action:** Auto-play Video 1 frames (0 to Max).  
* **GSAP Pseudo-code:**  
  JavaScript  
  // Reveal Canvas  
  gsap.to(canvasRef.current, { opacity: 1, duration: 1 });

  // Auto-play frames  
  gsap.to(frameObj, {  
    frame: maxFramesScene1,  
    snap: "frame",  
    duration: 3, // \~45 frames at 15fps  
    ease: "power2.out",  
    onUpdate: drawFrame  
  });

  // Fade in UI  
  gsap.to('.hero-ui-layer', { opacity: 1, y: 0, delay: 2.5, duration: 1 });

## **Scene 2: The Arsenal (Scroll Driven)**

* **Trigger:** User scrolls down into .scene-2-container.  
* **Action:** Scrub Video 2 frames. Trident moves right. Features stagger in.  
* **GSAP Pseudo-code:**  
  JavaScript  
  let tl \= gsap.timeline({  
    scrollTrigger: {  
      trigger: ".scene-2-container",  
      start: "top top",  
      end: "+=200%",  
      scrub: 0.5,  
      pin: true  
    }  
  });

  // Scrub video frames  
  tl.to(frameObj, {  
    frame: maxFramesScene2,  
    snap: "frame",  
    onUpdate: drawFrame  
  }, 0);

  // Stagger feature rows on the left  
  tl.fromTo(".feature-row",   
    { opacity: 0, x: \-50 },   
    { opacity: 1, x: 0, stagger: 0.1 },   
  0.2); // Start slightly after video begins moving

## **Scene 3: The Physics Pipeline (Scroll Driven)**

* **Trigger:** Scroll enters .scene-3-container.  
* **Action:** Crossfade from Canvas to static Y-Funnel image. Initialize Matter.js.  
* **GSAP Pseudo-code:**  
  JavaScript  
  ScrollTrigger.create({  
    trigger: ".scene-3-container",  
    start: "top center",  
    onEnter: () \=\> {  
      gsap.to(canvasRef.current, { opacity: 0, duration: 0.5 });  
      gsap.to('.physics-bg-layer', { opacity: 1, duration: 0.5 });  
      engine.world.gravity.y \= 1; // Start physics drop  
      spawnEmails();  
    },  
    onLeaveBack: () \=\> {  
      gsap.to(canvasRef.current, { opacity: 1, duration: 0.5 });  
      gsap.to('.physics-bg-layer', { opacity: 0, duration: 0.5 });  
    }  
  });

## **Scene 4: The Core Inspection (Click Triggered UI)**

* **Trigger:** onClick on .fraud-box-hitbox.  
* **Action:** Scroll locks. Background scales and blurs. Nested UI mounts.  
* **GSAP Pseudo-code:**  
  JavaScript  
  const openInbox \= (e) \=\> {  
    document.body.style.overflow \= "hidden"; // Lock scroll

    gsap.to('.physics-bg-layer', {  
      scale: 25,  
      transformOrigin: \`${e.clientX}px ${e.clientY}px\`, // Zoom into click coord  
      filter: "blur(10px) brightness(0.4)",  
      duration: 0.8,  
      ease: "power3.inOut"  
    });

    gsap.to('.inbox-overlay', { opacity: 1, scale: 1, duration: 0.5, delay: 0.4 });  
  };

## **Scene 5: The Engine Room (Interactive Terminal)**

* **Trigger:** Scroll enters .scene-5-container. Click on \[ EXECUTE \].  
* **Action:** Terminal slides up. On click, rapid typeout of logs and red flash.  
* **GSAP Pseudo-code:**  
  JavaScript  
  // Terminal Entrance  
  gsap.fromTo('.terminal-container',   
    { y: 100, opacity: 0 },   
    { y: 0, opacity: 1, scrollTrigger: { trigger: ".scene-5-container", start: "top 80%" }}  
  );

  // On Execute Click  
  const runBackendSim \= () \=\> {  
     simulateTypewriter(terminalLogs); // Custom typing utility

     // Triggered at the end of the log sequence  
     gsap.to('body', {   
       backgroundColor: "rgba(255,0,0,0.1)",   
       repeat: 3,   
       yoyo: true,   
       duration: 0.1   
     });  
  };

## **Scene 6: The Final Verdict (Scroll to End)**

* **Trigger:** Scroll reaches absolute bottom (.scene-6-container).  
* **Action:** Fade out terminal. Fade in Canvas running Video 3 (Loop). Fade in CTA.  
* **GSAP Pseudo-code:**  
  JavaScript  
  ScrollTrigger.create({  
    trigger: ".scene-6-container",  
    start: "top center",  
    onEnter: () \=\> {  
      gsap.to('.terminal-container', { opacity: 0, y: 50 });  
      gsap.to(canvasRef.current, { opacity: 1, duration: 1 });

      // Start looping Video 3  
      startHoverLoop(); 

      gsap.to('.final-cta-layer', { opacity: 1, y: 0, delay: 0.5 });  
    }  
  });

## ---

**4\. Data Structures**

## **mockEmails.js**

JavaScript

export const interceptedEmails \= \[  
  {  
    id: "evt\_9942a",  
    sender: "security-alert@amaz0n-verify.com",  
    subject: "URGENT: Your account has been compromised",  
    body: "Dear User,\\n\\nWe detected unauthorized access. \<span class='fraud-highlight'\>Click here immediately\</span\> to secure your account.\\n\\n- Amazon Support",  
    riskScore: 93,  
    classification: "CRITICAL",  
    campaignId: "cmp\_alpha\_01"  
  },  
  {  
    id: "evt\_9942b",  
    sender: "it-admin@corp-portal.net",  
    subject: "Mandatory Update Required",  
    body: "All employees must install the \<span class='fraud-highlight'\>attached security patch\</span\> by EOD.",  
    riskScore: 87,  
    classification: "HIGH",  
    campaignId: "cmp\_alpha\_01"  
  }  
\];

## **shapValues.js (For Threat Inspector Chart)**

JavaScript

export const shapData \= {  
  eventId: "evt\_9942a",  
  features: \[  
    { name: "Phishing ML Classifier", value: 0.38, impact: "negative" },  
    { name: "Malicious URL Detection", value: 0.29, impact: "negative" },  
    { name: "AI-Generated Text", value: 0.21, impact: "negative" },  
    { name: "Prompt Injection", value: 0.14, impact: "negative" },  
    { name: "Domain Reputation", value: \-0.05, impact: "positive" } // Slightly offsets score  
  \]  
};

## ---

**5\. Matter.js Physics Collider Setup**

To merge the dynamic physics with the static AI-generated Y-Funnel image, the Matter.js engine must utilize invisible static bodies (isStatic: true) mapped precisely to the glowing glass edges of the background image.

**Setup Instructions:**

1. **Overlay Canvas:** Create a \<canvas\> exactly the same dimensions as the static Y-funnel background image layer.  
2. **Invisible Boundaries:** Use Bodies.rectangle to create the walls.  
   * Set render: { visible: false } so the user only sees the image underneath.  
   * Set isStatic: true so the walls do not fall due to gravity.  
3. **Angle Mapping:**  
   * Use the angle property (in radians) to tilt the rectangles to match the V-shape of the funnel's interior basin.  
   * Example: Left slope angle: Math.PI / 6, Right slope angle: \-Math.PI / 6\.  
4. **The Split (Forking):**  
   * Place a static triangular body (Bodies.polygon) directly at the apex of the Y-split. This acts as the physical diverter.  
   * Apply a custom horizontal force (Body.applyForce) within the Events.on(engine, 'beforeUpdate') loop to gently push objects left or right based on their assigned "fraud" or "safe" properties once they hit the diverter.  
5. **Emitters:** Spawn the SVG email icons (Bodies.rectangle mapped to a sprite) at random x coordinates along the top edge of the canvas.