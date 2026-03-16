import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { gsap, Quint } from 'gsap';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';

export default function HeroSection() {
  const containerRef = useRef(null);
  const canvasWrapperRef = useRef(null);
  const loaderRef = useRef(null);

  useEffect(() => {
    if (!canvasWrapperRef.current) return;

    // --- Original App Class Logic Integrated ---
    class App {
      constructor() {
        this.init();
      }

      init() {
        this.group = new THREE.Object3D();
        this.gridSize = 40;
        this.buildings = [];
        this.fogConfig = {
          color: '#343c3c', // Matches CSS --color-bg
          near: 1,
          far: 208
        };

        this.width = window.innerWidth;
        this.height = window.innerHeight;

        this.createScene();
        this.createCamera();
        this.addFloor();
        this.addBackgroundShape();
        this.loadModels('/models/buildings.obj', this.onLoadModelsComplete.bind(this));
        
        this.pointLightObj3 = {
          color: '#d3263a',
          intensity: 15, // Adjusted for R180+ intensity scale
          position: { x: 16, y: 100, z: -68 }
        };
        this.addPointLight(this.pointLightObj3);
        
        this.animate();
        this.setupEvents();
      }

      createScene() {
        this.scene = new THREE.Scene();
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.width, this.height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        canvasWrapperRef.current.appendChild(this.renderer.domElement);
        this.scene.fog = new THREE.Fog(this.fogConfig.color, this.fogConfig.near, this.fogConfig.far);
      }

      createCamera() {
        this.camera = new THREE.PerspectiveCamera(20, this.width / this.height, 1, 1000);
        this.camera.position.set(3, 50, 155);
        this.scene.add(this.camera);
      }

      addBackgroundShape() {
        const planeGeometry = new THREE.PlaneGeometry(400, 100);
        const planeMaterial = new THREE.MeshPhysicalMaterial({ color: '#fff' });
        this.backgroundShape = new THREE.Mesh(planeGeometry, planeMaterial);
        this.backgroundShape.position.y = 10;
        this.backgroundShape.position.z = -150;
        this.scene.add(this.backgroundShape);

        this.mouseX = 3;
        this.lastMouseX = 3;
        this.lastMouseY = 65;
        this.lastScale = 155;
        
        // Line Equation mapping logic from app.js
        this.lineEq = (y2, y1, x2, x1, currentVal) => {
          let m = (y2 - y1) / (x2 - x1);
          let b = y1 - m * x1;
          return m * currentVal + b;
        };
        this.lerp = (a, b, n) => (1 - n) * a + n * b;

        this.updateDocHeight();
      }

      updateDocHeight() {
        this.docheight = Math.max(
          document.body.scrollHeight, 
          document.body.offsetHeight, 
          document.documentElement.clientHeight, 
          document.documentElement.scrollHeight, 
          document.documentElement.offsetHeight
        );
      }

      setupEvents() {
        this.onMouseMove = (ev) => {
          this.mouseX = ev.clientX;
        };

        this.onResize = () => {
          this.width = window.innerWidth;
          this.height = window.innerHeight;
          this.camera.aspect = this.width / this.height;
          this.camera.updateProjectionMatrix();
          this.renderer.setSize(this.width, this.height);
          this.updateDocHeight();
        };

        window.addEventListener('mousemove', this.onMouseMove);
        window.addEventListener('resize', this.onResize);
      }

      tilt() {
        // Camera movement logic tied to scroll and mouse
        this.lastMouseX = this.lerp(this.lastMouseX, this.lineEq(6, 0, this.width, 0, this.mouseX), 0.05);
        const newScrollingPos = window.pageYOffset;
        this.lastMouseY = this.lerp(this.lastMouseY, this.lineEq(0, 65, this.docheight, 0, newScrollingPos), 0.05);
        this.lastScale = this.lerp(this.lastScale, this.lineEq(0, 158, this.docheight, 0, newScrollingPos), 0.05);
        
        this.camera.position.set(this.lastMouseX, this.lastMouseY, this.lastScale);
        this.camera.lookAt(0, 0, 0);
      }

      addFloor() {
        const planeGeometry = new THREE.PlaneGeometry(200, 200);
        const planeMaterial = new THREE.MeshStandardMaterial({
          color: '#000000',
          metalness: 0,
          roughness: 0,
        });
        const plane = new THREE.Mesh(planeGeometry, planeMaterial);
        plane.rotateX(-Math.PI / 2);
        plane.position.y = 0;
        this.scene.add(plane);
      }

      addPointLight(params) {
        const pointLight = new THREE.PointLight(params.color, params.intensity);
        pointLight.position.set(params.position.x, params.position.y, params.position.z);
        this.scene.add(pointLight);
      }

      loadModels(url, callback) {
        const objLoader = new OBJLoader();
        objLoader.load(url, callback);
      }

      onLoadModelsComplete(obj) {
        this.models = [...obj.children].map((model) => {
          model.scale.set(0.01, 0.01, 0.01);
          model.position.set(0, -14, 0);
          model.receiveShadow = true;
          model.castShadow = true;
          return model;
        });

        this.draw();

        setTimeout(() => {
          if (loaderRef.current) loaderRef.current.classList.add('loader--done');
          this.showBuildings();
        }, 500);
      }

      draw() {
        const boxSize = 3;
        const material = new THREE.MeshPhysicalMaterial({
          color: '#000',
          metalness: 0,
          roughness: 0.77,
        });

        for (let i = 0; i < this.gridSize; i++) {
          for (let j = 0; j < this.gridSize; j++) {
            const building = this.models[Math.floor(Math.random() * this.models.length)].clone();
            building.material = material;
            building.scale.y = Math.random() * (0.01); // max .009 + .01 simplified
            building.position.x = i * boxSize;
            building.position.z = j * boxSize;
            this.group.add(building);
            this.buildings.push(building);
          }
        }

        this.group.position.set(-this.gridSize - 10, 1, -this.gridSize - 10);
        this.scene.add(this.group);
      }

      showBuildings() {
        this.buildings.sort((a, b) => b.position.z - a.position.z);
        this.buildings.forEach((building, index) => {
          gsap.to(building.position, {
            y: 1,
            duration: 0.6 + (index / 4000),
            ease: "quint.out",
            delay: index / 4000
          });
        });
      }

      animate() {
        this.tilt();
        this.renderer.render(this.scene, this.camera);
        this.requestID = requestAnimationFrame(this.animate.bind(this));
      }

      destroy() {
        cancelAnimationFrame(this.requestID);
        window.removeEventListener('mousemove', this.onMouseMove);
        window.removeEventListener('resize', this.onResize);
        if (this.renderer) {
          this.renderer.dispose();
          if (canvasWrapperRef.current && this.renderer.domElement) {
            canvasWrapperRef.current.removeChild(this.renderer.domElement);
          }
        }
      }
    }

    const app = new App();

    return () => {
      app.destroy();
    };
  }, []);

  return (
    <div ref={containerRef} className="hero-container relative">
      {/* 1:1 SVG Loader from original index.html */}
      <div ref={loaderRef} className="loader">
        <svg className="loader__icon" width="100" height="105" viewBox="0 0 100 105">
          <g>
            <path d="M18.605 20.909l26.375 8.01 1.317-4.339L18.041 16 5.483 23.247l2.266 3.926z" />
            <path d="M18.605 28.909l26.375 8.01 1.317-4.339L18.041 24 5.483 31.247l2.266 3.926z" />
            <path d="M18.605 36.909l26.375 8.01 1.317-4.339L18.041 32 5.483 39.247l2.266 3.926z" />
            <path d="M18.605 44.909l26.375 8.01 1.317-4.339L18.041 40 5.483 47.247l2.266 3.926z" />
            <path d="M18.605 52.909l26.375 8.01 1.317-4.339L18.041 48 5.483 55.246l2.266 3.927z" />
            <path d="M18.605 60.909l26.375 8.01 1.317-4.339L18.041 56 5.483 63.246l2.266 3.927z" />
            <path d="M18.605 68.909l26.375 8.01 1.317-4.339L18.041 64 5.483 71.246l2.266 3.927z" />
            <path d="M18.605 76.909l26.375 8.01 1.317-4.339L18.041 72 5.483 79.246l2.266 3.927z" />
          </g>
          <g>
            <path d="M61.689 4.909l26.375 8.01 1.317-4.339L61.125 0 48.567 7.247l2.266 3.926z" />
            <path d="M61.689 12.909l26.375 8.01 1.317-4.339L61.125 8l-12.558 7.247 2.266 3.926z" />
            <path d="M61.689 20.909l26.375 8.01 1.317-4.339L61.125 16l-12.558 7.247 2.266 3.926z" />
            <path d="M61.689 28.909l26.375 8.01 1.317-4.339L61.125 24l-12.558 7.247 2.266 3.926z" />
            <path d="M61.689 36.909l26.375 8.01 1.317-4.339L61.125 32l-12.558 7.247 2.266 3.926z" />
            <path d="M61.689 44.909l26.375 8.01 1.317-4.339L61.125 40l-12.558 7.247 2.266 3.926z" />
            <path d="M61.689 52.909l26.375 8.01 1.317-4.339L61.125 48l-12.558 7.246 2.266 3.927z" />
            <path d="M61.689 60.909l26.375 8.01 1.317-4.339L61.125 56l-12.558 7.246 2.266 3.927z" />
            <path d="M61.689 68.909l26.375 8.01 1.317-4.339L61.125 64l-12.558 7.246 2.266 3.927z" />
            <path d="M61.689 76.909l26.375 8.01 1.317-4.339L61.125 72l-12.558 7.246 2.266 3.927z" />
          </g>
        </svg>
      </div>

      <div className="frame">
        <div className="frame__title-wrap">
          <h1 className="frame__title">Buildings Wave Animation</h1>
        </div>
        <div className="frame__credits">
          Models by <a href="https://free3d.com/3d-model/19-low-poly-buildings-974347.html" target="_blank" rel="noopener noreferrer">Backlog Studio</a>
        </div>
        <div className="frame__links">
          <a href="#">Previous Demo</a>
          <a href="#">Article</a>
          <a href="#">GitHub</a>
        </div>
        <div className="frame__scroll">scroll</div>
        <div className="frame__demos">
          <a href="#" className="frame__demo frame__demo--current">1</a>
          <a href="#" className="frame__demo">2</a>
        </div>
      </div>

      <div ref={canvasWrapperRef} className="canvas-wrapper"></div>

      <div className="content">
        <h2 className="content__title">
          <span className="content__title-inner">Resistance</span>
          <span className="content__title-sub">106.4 FM</span>
        </h2>
      </div>

      <div className="content content--final">
        <p className="content__text">
          Building 1278<br />
          107 Hafnarbraut Road<br />
          50X8 Paradise Falls<br />
          New California
        </p>
      </div>
    </div>
  );
}
