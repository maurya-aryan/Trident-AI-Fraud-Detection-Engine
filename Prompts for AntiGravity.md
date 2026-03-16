# **MAGE / FRAME GENERATION PROMPTS (WpDev Keyboard \+ Fog Background)**

## **1\) HERO SHOT (single frame / key visual)**

Cinematic product shot of a tangerine-orange mechanical keyboard with off-white and light gray keycaps, “WpDev”, floating on soft white clouds, light gray studio fog background, premium diffused lighting, 4k, photorealistic.

---

## **2\) ULTRA-PREMIUM PRODUCT PHOTOGRAPHY (assembled keyboard)**

Ultra-premium product photography of a sleek **tangerine-orange / amber anodized aluminum mechanical keyboard** called “WpDev” resting within **soft white clouds / volumetric fog**, minimalistic editorial studio photoshoot. Background is **light gray-to-white mist** with gentle gradient falloff, airy and clean. Soft diffused key light with subtle rim highlights outlining the keyboard silhouette, **keycap edges**, and the **rotary knob** on the top-right. Controlled reflections on the orange metal case; crisp detail on **off-white and light gray keycaps** with a few matching orange accent keys. Shallow depth of field, sharp focus on the keyboard, cinematic but bright, luxury modern hardware aesthetic. No clutter, no text overlays, no logos emphasized. Shot with a professional DSLR, 85mm lens, f/2.0, ultra-high resolution, photorealistic, premium editorial product photography.

---

## **3\) LAYERED “OPENING” ENGINEERING VIEW (for the scroll sequence look)**

Exploded **layer-separated engineering view** of the same “WpDev” keyboard with a **tangerine-orange anodized aluminum chassis**, every layer precisely separated and floating in perfect alignment, suspended in mid-air within **soft white/gray studio fog and cloud haze**. Show the keyboard opening into clean layers: **off-white \+ light gray keycaps**, switches, top plate, PCB, stabilizers, foam layers, controller, USB-C daughterboard, bottom case, screws, and the **rotary knob assembly**—all centered, evenly spaced, perfectly aligned. Lighting matches the hero: soft diffused illumination with gentle rim highlights, controlled reflections on orange metal and matte plastics. Editorial engineering aesthetic, ultra-sharp focus, photorealistic, ultra-high resolution. **No labels, no annotations, no text.**

---

## **4\) MOTION / SEQUENCE DIRECTION (what the 120 frames should do)**

Create a 120-frame sequence where the keyboard performs a **scroll-friendly mechanical “expand → open → reassemble”** action:

* **Frames 0–20:** Keyboard fully assembled, centered, stable.

* **Frames 21–55:** Keyboard **subtly expands outward** (precision widening / spacing cues), still mostly assembled.

* **Frames 56–85:** Keyboard **opens into layers** (keycaps/switches/plate/PCB/case visible), all aligned, clean separations.

* **Frames 86–119:** Layers glide back together and keyboard returns fully assembled.

Motion feels **magnetic, engineered, controlled**, with gentle easing. No jitter. No dramatic spins. Keep camera angle consistent across frames. Keep fog/cloud background consistent and soft.

---

# **GOOGLE ANTIGRAVITY – MASTER WEBSITE PROMPT (Scrollytelling)**

**ACT AS:**  
 A world-class Creative Developer (Awwwards-level) specializing in Next.js, Framer Motion, and high-performance scrollytelling.

---

## **THE TASK**

Build a high-end “Scrollytelling” landing page for a fictional keyboard brand called **“WpDev”**.

The core mechanic is a **scroll-linked animation** that plays an image sequence of the **WpDev keyboard expanding and opening into layers**, then **closing/reassembling** as the user reaches the end of the scroll.

---

## **TECH STACK**

* Framework: **Next.js 14 (App Router)**

* Styling: **Tailwind CSS**

* Animation: **Framer Motion**

* Rendering: **HTML5 Canvas** (for performance)

---

## **VISUAL DIRECTION (Fog / Editorial Light Theme)**

* **Seamless Blending:** The website background MUST match the **fog/mist background** of the image sequence exactly so the edges of frames are invisible.

* **Background Color:** Use an eyedropped fog color (example: `#ECECEC` / `#E6E6E6`). The exact value should match the frames.

* **Typography:** Inter or San Francisco. Minimal, tracking-tight.

* **Text Color:** Because the page is light:

  * Headings: `text-black/90`

  * Body: `text-black/60`

* **Aesthetic:** Premium editorial hardware. Clean, quiet, high-end. No noisy gradients. No unnecessary UI clutter.

---

## **IMPLEMENTATION DETAILS**

### **1\) The Sticky Canvas**

* Create a component: `components/KeyboardScroll.tsx`

* Outer container: `h-[400vh]` to create a long scroll.

* Inside: a `<canvas>` that is:

  * `sticky top-0 h-screen w-full`

  * perfectly centered

* Canvas should render frames sharply (handle devicePixelRatio).

---

### **2\) Image Sequence Loading**

* Load a sequence of **120 images** (0 → 119\) exported from `ezgif-split`.

* Naming convention: `frame_[i]_delay-0.04s.webp`

* Preload all images before playing to avoid flicker.

* Show a loading spinner/progress indicator until enough frames are ready (ideally all frames).

---

### **3\) Scroll → Frame Mapping (Correct \+ Smooth)**

* Use `useScroll` from Framer Motion to map scroll progress (0 → 1\) to frame index (0 → 119).

* On scroll:

  * compute current frame index

  * draw the image to canvas using `requestAnimationFrame`

* Clamp frame index and avoid redundant draws to reduce jank.

**Canvas draw behavior:**

* Use a “contain” fit so the keyboard stays fully visible across screen sizes.

* Keep consistent positioning so the keyboard doesn’t jump between frames.

* Recalculate canvas size on resize.

---

### **4\) Story Text Overlays (Timed Fade In/Out)**

Overlay text sections that fade in/out as the keyboard expands/opens.

Use these exact beats:

* **0% Scroll (Centered):**  
   **“WpDev Keyboard.”**  
   subtext: “Engineered clarity.”

* **25% Scroll (Left aligned):**  
   **“Built for Precision.”**  
   subtext: “Every detail, measured.”

* **60% Scroll (Right aligned):**  
   **“Layered Engineering.”**  
   subtext: “See what’s inside.”

* **90% Scroll (Centered CTA):**  
   **“Assembled. Ready.”**  
   subtext: “Scroll back to replay.”

Text styling rules:

* Keep type large, minimal, and spaced.

* Use subtle fade \+ slight translate (like `y: 10px → 0px`).

* Never block the keyboard center; keep overlays out of the main product area.

---

### **5\) Polish Requirements**

* Loading state: centered spinner \+ “Loading WpDev sequence…” (subtle).

* Smoothness:

  * avoid stutter

  * avoid flashing backgrounds

  * avoid layout shift

* Mobile:

  * Canvas should scale and keep keyboard fully visible (contain fit).

  * Text overlays should reposition gracefully (no overlap).

---

## **OUTPUT**

Generate the full code for:

* `app/page.tsx`

* `components/KeyboardScroll.tsx`

* `app/globals.css`

**Use nano banana** to generate any UI components if needed, but keep the UI minimal.

---

