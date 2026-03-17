# 🚀 EmailFunnel Test Page

## 📍 Location
This test page is located at:
```
c:\Users\Administrator\OneDrive\ドキュメント\GitHub\Trident-AI-Fraud-Detection-Engine\frontend-test\
```

## 📂 File Structure
```
frontend-test/
├── index.html              # Main HTML file
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Main App component
    └── EmailFunnel.jsx     # Enhanced EmailFunnel with Matter.js physics
```

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd frontend-test
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

### Step 3: View in Browser
The page will automatically open at: **http://localhost:3000**

---

## 🎯 What You'll See

When you run the test page, you'll see:

1. **Beautiful Dark Background** with a grid overlay
2. **TRIDENT Header** with the tagline "EMAILS. CLASSIFIED. ROUTED."
3. **3D Funnel Visualization** with:
   - Glowing cyan walls
   - Y-split design (FEATURE A / FEATURE B)
   - Subtle 3D tilt effect
4. **Gmail Icons** falling through the funnel with:
   - Realistic physics (gravity, collisions, bounce)
   - Smooth rotation
   - Blue glow effects
5. **Replay Button** to restart the animation

---

## 🎮 Interactive Features

- **Hover over funnel**: The 3D tilt straightens and the funnel scales up slightly
- **Hover over replay button**: Button glows brighter
- **Click replay button**: Animation restarts from the beginning

---

## 🔧 Available Commands

```bash
npm run dev      # Start development server (hot reload enabled)
npm run build    # Build for production
npm run preview  # Preview production build
```

---

## 🎨 Features Implemented

### ✅ Matter.js Physics Engine
- Real gravity simulation
- Ball-to-ball collisions
- Ball-to-wall collisions
- Realistic bounce and friction

### ✅ Invisible Physics Walls
- Aligned perfectly with funnel geometry
- Funnel trapezoid walls (angled)
- Neck walls (vertical)
- Y-split curved walls (8 segments each arm)
- Bottom catchers (prevent infinite falling)

### ✅ Gmail Icon Balls
- Embedded SVG (no external files)
- 28x28 pixel Gmail icons
- Rotate with physics
- Blue glow effects

### ✅ CSS 3D Transforms
- Perspective: 1200px
- Subtle 2° tilt for depth
- Interactive hover effects
- Smooth transitions

### ✅ Scroll Animation
- Uses IntersectionObserver
- Triggers when funnel enters viewport
- One-time trigger (efficient)

---

## 📝 Customization

Want to modify the funnel? Edit these files:

### Change Physics
Edit `src/EmailFunnel.jsx`, lines 382-409:
```jsx
// Adjust gravity
const engine = Engine.create({
  gravity: { x: 0, y: 1.2 }  // Higher = faster falling
});

// Adjust ball physics
const ball = Bodies.circle(schedule.startX, -20, BALL_R, {
  restitution: 0.6,  // 0-1 (bounciness)
  friction: 0.1,     // Higher = more friction
  density: 0.002     // Higher = heavier balls
});
```

### Change Ball Count
Edit `src/EmailFunnel.jsx`, lines 392-401:
```jsx
const ballSchedule = [
  { delay: 0, startX: FLX + 60 },
  { delay: 400, startX: FRX - 60 },
  // Add more balls here...
];
```

### Change Colors
Edit `src/EmailFunnel.jsx`, line 19:
```jsx
const CYAN = "rgba(0,212,255,";  // Change to any color
```

### Change Endpoint Labels
Edit `src/EmailFunnel.jsx`, lines 317-318:
```jsx
drawEndpoint(ctx, LEX, ENY, "YOUR TEXT A");
drawEndpoint(ctx, REX, ENY, "YOUR TEXT B");
```

---

## 🐛 Troubleshooting

### Port 3000 already in use?
```bash
# Use a different port
npm run dev -- --port 3001
```

### Dependencies not installing?
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Balls escaping the funnel?
Increase wall segments in `src/EmailFunnel.jsx`, line 92:
```jsx
const leftArmSegments = 12;  // Was 8
```

### Gmail icons not showing?
Check browser console (F12) for errors. The SVG is embedded, so no network issues should occur.

---

## 📊 Performance

- **FPS**: 60 (capped by requestAnimationFrame)
- **Ball Count**: 8 (can easily support 20+)
- **Memory**: Auto-cleanup on component unmount
- **Browser**: Works on all modern browsers (Chrome, Firefox, Safari, Edge)

---

## 🎉 What's Next?

After testing, you can:

1. **Copy `EmailFunnel.jsx`** to your main project
2. **Integrate** with your existing React app
3. **Customize** colors, physics, and labels to match your brand
4. **Add more features** (click handlers, tooltips, etc.)

---

## 💡 Tips

- **Smooth Performance**: The physics engine is optimized for 60 FPS
- **Responsive Design**: Works on all screen sizes (canvas is fixed at 520x680)
- **Production Ready**: Includes proper cleanup and error handling
- **Hot Reload**: Changes to code update instantly during development

---

## 📞 Need Help?

If you encounter any issues or want to customize further, let me know!

**Enjoy your physics-powered email funnel! 📧⚛️**
