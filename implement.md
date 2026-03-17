# TRIDENT - AI Fraud Detection Engine: Hero Section Implementation

## 1. Overview & Objective
We are building a highly immersive, scroll-driven 3D hero section. The environment will consist of a dark-mode procedural 3D cityscape that reacts to the user's scroll position, paired with an HTML/CSS UI layer. 

## 2. Core Dependencies
* **WebGL/3D Generation:** Three.js `@react-three/fiber` / `@react-three/drei` (recommended for React) or standard vanilla Three.js inside a `useEffect`.
* **Scroll Animation:** GSAP 3 & GSAP `ScrollTrigger` plugin.
* **3D Assets:** 
  * `gold trident (1).glb` (Trident model): Located in the project root.
  * `buildings.obj` (Procedural city mesh): Located at `inspiration/buildings-wave/with-controls/buildings.obj`. We will import and clone this base mesh to generate the server city array.

## 3. Visual Aesthetic Theme
* **Environment:** Pure black foggy atmosphere (`scene.fog` and `renderer.setClearColor` set to `#000000`).
* **Buildings:** `MeshStandardMaterial` for our procedural buildings with dark gray base, high metalness, and neon emissive glows (cyan/danger red) simulating data servers.
* **UI:** Sleek, glassmorphic dark-mode cybersecurity widgets overlaid upon the canvas (`z-index` placed above).

## 4. Scroll Choreography (Mapped to 400vh Scroll Container)

### Phase 1: The Emergence (0% - 30% Scroll)
* **Start:** Trident model hidden (`position.y = -10`) below the glowing server buildings. The HTML main title ("TRIDENT - AI Fraud Detection Engine") has `opacity: 0`. The camera looks down the street (`camera.position.z` is far back).
* **Action:** As user scrolls, the Gold Trident rises to screen center (`position.y = 0`) and gently rotates. Simultaneously, the main HTML title fades in.

### Phase 2: The Interception & Parallax Zoom (30% - 70% Scroll)
* **Start:** Title slowly fades out.
* **Action:** The Trident shoots rapidly off-screen upwards (`position.y = 20`). 
* **The Zoom Effect:** Upon the Trident's exit, GSAP ScrollTrigger aggressively decreases the camera's Z-position (`camera.position.z -= <high value>`). This causes the camera to physically fly *forward* through the 3D server columns we generated, creating an intense, physical 3D parallax "hack-in" or "space-tunnel" zoom effect, rather than a flat CSS scale.

### Phase 3: The Arsenal (70% - 100% Scroll)
* **Start:** Forward camera motion halts. The entire 3D background subtly dims.
* **Action:** A staggered fade-in of an HTML/CSS Grid displaying 9 cybersecurity feature cards (Credential Exposure, Malware Scanner, Email Phishing, URL Detection, etc.) over the canvas.

## 5. Development Strategy (React/Vite Adaptation)
We will implement this architecture directly via React components in the `./frontend` directory:
1. **Canvas Component:** Initialize Three.js (`scene`, `camera`, `renderer`) locally.
2. **Procedural Geometry:** Load the local `buildings.obj`, apply the dark-mode `MeshStandardMaterial`, and duplicate/distribute it in a grid using pure JS math (similar to the inspiration repo's `app.js` logic).
3. **Scroll Container Setup:** Create a container of height `400vh` and bind it to a master GSAP ScrollTrigger timeline.
4. **GSAP Tweens:** Animate `trident.position.y` and `camera.position.z` hooked into the ScrollTrigger progress.
5. **DOM UI Overlay:** Map the 9 cybersecurity features to styled React components absolutely positioned over the canvas, using GSAP to independently stagger their opacity.
