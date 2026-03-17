import React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import Storm from "./Storm";

function App() {
    return (
        <div className="App">
            <div className="canvas-container">
                <Canvas
                    camera={{ position: [0, 5, 12], fov: 60 }}
                    style={{ background: "#151515" }}
                >
                    <ambientLight intensity={0.3} />
                    <directionalLight position={[10, 10, 5]} intensity={0.5} />
                    <Storm />
                    <OrbitControls
                        enablePan={true}
                        enableZoom={true}
                        enableRotate={true}
                    />
                </Canvas>
            </div>
        </div>
    );
}

export default App;
