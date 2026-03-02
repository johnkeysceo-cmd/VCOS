"""
Recording Service - ScreenArc Launcher
Launches ScreenArc for video recording
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# ScreenArc paths
SCREENARC_ROOT = Path(__file__).parent.parent.parent.parent / "generation_content" / "screenarc"

class ScreenArcLauncher:
    """Launches ScreenArc for recording"""
    
    def __init__(self):
        self.screenarc_root = SCREENARC_ROOT
        self.node_available = self._check_node()
    
    def _check_node(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def launch_recording(
        self,
        output_directory: str,
        preset: str = "cinematic"
    ) -> Dict:
        """
        Launch ScreenArc for recording
        
        Args:
            output_directory: Directory to save recorded video
            preset: ScreenArc preset to use
            
        Returns:
            Launch result
        """
        if not self.node_available:
            return {
                "success": False,
                "error": "Node.js not available. Install Node.js to use ScreenArc."
            }
        
        if not self.screenarc_root.exists():
            return {
                "success": False,
                "error": f"ScreenArc not found at {self.screenarc_root}"
            }
        
        # Try to launch ScreenArc GUI or CLI recording
        # Check for package.json to see available scripts
        package_json = self.screenarc_root / "package.json"
        
        if package_json.exists():
            # Try npm script for recording
            try:
                logger.info(f"Launching ScreenArc recording to: {output_directory}")
                
                # Set output directory environment variable
                env = os.environ.copy()
                output_dir_abs = str(Path(output_directory).resolve())
                env["VCOS_OUTPUT_DIR"] = output_dir_abs
                env["SCREENARC_OUTPUT_DIR"] = output_dir_abs
                env["VCOS_AUTO_LAUNCH"] = "true"  # Auto-open recorder window
                
                # Set VCOS export directory (where exported videos go)
                export_dir = Path(__file__).parent.parent.parent.parent / "data" / "exports"
                export_dir.mkdir(parents=True, exist_ok=True)
                env["VCOS_EXPORT_DIR"] = str(export_dir)
                
                # Check if app is built (dist-electron exists)
                dist_electron = self.screenarc_root / "dist-electron" / "index.js"
                
                if dist_electron.exists():
                    # Launch built Electron app
                    logger.info("Launching built ScreenArc app...")
                    electron_path = self.screenarc_root / "node_modules" / ".bin" / "electron"
                    if platform.system() == "Windows":
                        electron_path = electron_path.with_suffix(".cmd")
                    
                    if electron_path.exists():
                        subprocess.Popen(
                            [str(electron_path), str(dist_electron)],
                            cwd=str(self.screenarc_root),
                            env=env,
                            shell=False
                        )
                    else:
                        # Fallback to npm run dev
                        logger.info("Electron binary not found, using npm run dev...")
                        subprocess.Popen(
                            ["npm", "run", "dev"],
                            cwd=str(self.screenarc_root),
                            env=env,
                            shell=True,
                            creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                        )
                else:
                    # App not built, use dev mode
                    logger.info("App not built, launching in dev mode...")
                    logger.info("Note: First launch may take longer. Building app...")
                    subprocess.Popen(
                        ["npm", "run", "dev"],
                        cwd=str(self.screenarc_root),
                        env=env,
                        shell=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                    )
                
                return {
                    "success": True,
                    "message": "ScreenArc launched. Record your video and save to the output directory.",
                    "output_directory": output_directory
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to launch ScreenArc: {e}"
                }
        else:
            return {
                "success": False,
                "error": "ScreenArc package.json not found"
            }
    
    def check_setup(self) -> Dict:
        """Check ScreenArc setup"""
        return {
            "screenarc_exists": self.screenarc_root.exists(),
            "node_available": self.node_available,
            "ready": self.node_available and self.screenarc_root.exists()
        }

# Global launcher
screenarc_launcher = ScreenArcLauncher()
