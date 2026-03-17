# Role & Objective
You are an expert creative front-end developer specializing in WebGL, Three.js, and GSAP. 
I need you to build a scroll-driven 3D hero section for my project: "TRIDENT - AI Fraud Detection Engine".

# The Architecture
We are building a fixed 3D canvas background with an HTML/CSS UI layer overlaid on top. The animation must be driven entirely by the user's scroll position using GSAP 3's `ScrollTrigger`. 

We will adapt the procedural 3D city generation logic from this repository: `https://github.com/iondrimba/buildings-wave.git`.
* **Remove:** The legacy `TweenMax` animations and the continuous waving loop.
* **Keep:** The procedural grid generation of the `THREE.InstancedMesh` buildings.
* **Add:** GSAP 3, ScrollTrigger, and `GLTFLoader`.

# Visual Theme (Cybersecurity / Dark Mode)
* **Buildings:** Override the original building materials. Use a `MeshStandardMaterial` with a very dark grey/black base color. Turn up the `metalness` and add a neon `emissive` color (like cyan or danger red) so they look like glowing data servers.
* **Atmosphere:** Set the `scene.fog` color and the `renderer.setClearColor` to pure black (`#000000`).
* **Assets:** I will provide a `trident.glb` model. Load it using `GLTFLoader` and place it at the center of the scene (`x: 0, z: 0`).

# The Scroll Choreography
Set up a fixed `<canvas>` and a tall, invisible scroll container (e.g., `400vh`) to allow for a long scroll timeline. Map the following timeline strictly to the scroll progress:

**Phase 1: The Emergence (Scroll 0% -> 30%)**
* **Initial State:** The `trident.glb` is hidden below the ground (`position.y = -10`). The HTML main title ("TRIDENT - AI Fraud Detection Engine") has `opacity: 0`. The camera looks slightly down the street.
* **Animation:** As the user scrolls, the Trident rises to `position.y = 0` (center frame) and slowly rotates. Simultaneously, the HTML title fades to `opacity: 1`.

**Phase 2: The Interception & Zoom (Scroll 30% -> 70%)**
* **Animation:** The HTML title fades out. The Trident shoots upwards (`position.y = 20`, exiting the top of the screen). 
* **Camera:** Immediately as the Trident leaves, aggressively decrease the camera's Z-position (`camera.position.z`) to fly rapidly forward *through* the dark 3D buildings, creating a high-speed parallax zoom effect.

**Phase 3: The Arsenal (Scroll 70% -> 100%)**
* **Animation:** The camera stops its forward motion. The 3D background dims slightly (or fades opacity). 
* **UI Reveal:** An HTML/CSS Grid containing 9 feature cards stagger-fades into view over the canvas.

# The HTML Overlay Content
The Phase 3 feature cards must be styled as sleek, dark-mode cybersecurity widgets. The 9 cards are:
1. Credential Exposure
2. Malware Scanner
3. AI Text Detection
4. Email Phishing
5. URL Detection
6. Prompt Injection
7. Fusion Model
8. Campaign Graph
9. SHAP Explainer

# Deliverables Requested
Please provide the complete, ready-to-run code including:
1.  `index.html` (Canvas setup and UI overlays)
2.  `style.css` (Positioning for the pinned canvas and the CSS Grid for the 9 cards)
3.  `main.js` (Three.js setup, building generation, GLTFLoader logic, and the GSAP ScrollTrigger timeline)