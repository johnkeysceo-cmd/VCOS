"""
Recording Service - ScreenArc Comprehensive Wrapper
Complete wrapper for starting and controlling ScreenArc via terminal
"""

import os
import subprocess
import json
import time
import platform
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# ScreenArc paths
SCREENARC_ROOT = Path(__file__).parent.parent.parent.parent / "generation_content" / "screenarc"
SCREENARC_CLI = SCREENARC_ROOT / "scripts" / "screenarc-cli.cjs"
SCREENARC_NPM_SCRIPT = "cli:process"

class ScreenArcWrapper:
    """Comprehensive wrapper for ScreenArc CLI operations"""
    
    def __init__(self):
        self.screenarc_root = SCREENARC_ROOT
        self.cli_path = SCREENARC_CLI
        self.node_available = self._check_node()
        self.npm_available = self._check_npm()
    
    def _check_node(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"Node.js available: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        logger.warning("Node.js not found. Install Node.js to use ScreenArc CLI.")
        return False
    
    def _check_npm(self) -> bool:
        """Check if npm is available"""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"npm available: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        return False
    
    def start_screenarc_cli(
        self,
        input_video: str,
        output_video: str,
        preset: str = "cinematic",
        metadata_path: Optional[str] = None,
        **options
    ) -> Dict:
        """
        Start ScreenArc CLI processing
        
        Args:
            input_video: Input video path
            output_video: Output video path
            preset: Preset name
            metadata_path: Optional metadata JSON
            **options: Additional ScreenArc options
            
        Returns:
            Processing result
        """
        if not self.node_available:
            return {
                "success": False,
                "error": "Node.js not available. Install Node.js to use ScreenArc."
            }
        
        # Try direct CLI script first
        if self.cli_path.exists():
            return self._run_cli_script(input_video, output_video, preset, metadata_path, timeout=300, **options)
        
        # Fallback to npm script
        if self.npm_available:
            return self._run_npm_script(input_video, output_video, preset, metadata_path, **options)
        
        return {
            "success": False,
            "error": "ScreenArc CLI not found. Check generation_content/screenarc exists."
        }
    
    def _run_cli_script(
        self,
        input_video: str,
        output_video: str,
        preset: str,
        metadata_path: Optional[str],
        timeout: int = 300,
        **options
    ) -> Dict:
        # Calculate timeout based on video duration - AGGRESSIVE timeouts
        # For small videos (< 10s), use very short timeout (30s)
        # For longer videos, use proportional timeout (duration * 5, max 120s)
        try:
            import cv2
            cap = cv2.VideoCapture(input_video)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            if video_duration < 10:
                timeout = 30  # 30 seconds for short videos - AGGRESSIVE
            elif video_duration < 30:
                timeout = min(int(video_duration * 5), 90)  # 5x duration, max 90s
            else:
                timeout = min(int(video_duration * 4), 120)  # 4x duration, max 2 min
            logger.info(f"Calculated timeout: {timeout}s for {video_duration:.1f}s video")
        except Exception as e:
            # If we can't determine duration, use very short default
            timeout = 30
            logger.warning(f"Could not determine video duration, using {timeout}s timeout: {e}")
        """Run ScreenArc CLI script directly"""
        # Convert to absolute paths to avoid path resolution issues
        input_video_abs = str(Path(input_video).resolve())
        output_video_abs = str(Path(output_video).resolve())
        
        # Ensure output directory exists
        Path(output_video_abs).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "node",
            str(self.cli_path),
            "process",
            "-i", input_video_abs,
            "-o", output_video_abs,
            "-p", preset
        ]
        
        if metadata_path and os.path.exists(metadata_path):
            cmd.extend(["-m", metadata_path])
        
        # Add additional options
        for key, value in options.items():
            key = key.replace("_", "-")
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            else:
                cmd.extend([f"--{key}", str(value)])
        
        try:
            logger.info(f"Running ScreenArc CLI: {' '.join(cmd)}")
            start_time = time.time()
            
            # Use Popen for better control and to avoid hanging
            process = subprocess.Popen(
                cmd,
                cwd=str(self.screenarc_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Wait for process with timeout, checking frequently
            elapsed = 0
            check_interval = 2  # Check every 2 seconds (more frequent)
            
            while elapsed < timeout:
                returncode = process.poll()
                if returncode is not None:
                    # Process finished
                    elapsed = time.time() - start_time
                    stdout, stderr = process.communicate()  # Get remaining output
                    
                    if returncode == 0:
                        # Verify output file actually exists
                        if os.path.exists(output_video_abs):
                            logger.info(f"ScreenArc CLI completed successfully in {elapsed:.1f}s")
                            return {
                                "success": True,
                                "output_path": output_video_abs,
                                "processing_time": elapsed,
                                "stdout": stdout
                            }
                        else:
                            logger.warning(f"ScreenArc CLI completed but output file not found: {output_video_abs}")
                            return {
                                "success": False,
                                "error": f"Output file not created: {output_video_abs}"
                            }
                    else:
                        error_msg = stderr or stdout or f"Process exited with code {returncode}"
                        logger.error(f"ScreenArc CLI failed: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "returncode": returncode
                        }
                
                time.sleep(check_interval)
                elapsed = time.time() - start_time
                
                # Log progress every 10 seconds (more frequent)
                if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                    logger.info(f"ScreenArc CLI still processing... ({elapsed:.0f}s / {timeout}s)")
                
                # If timeout is approaching, warn
                if elapsed > timeout * 0.7:
                    logger.warning(f"ScreenArc CLI approaching timeout ({elapsed:.0f}s / {timeout}s) - will terminate soon")
            
            # Timeout reached - KILL IT
            logger.error(f"ScreenArc CLI TIMED OUT after {timeout}s - FORCE KILLING process")
            try:
                process.terminate()
                # Give it 3 seconds to die gracefully
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't die
                    logger.warning("Process didn't terminate, force killing...")
                    process.kill()
                    process.wait(timeout=2)
            except Exception as e:
                logger.error(f"Error killing process: {e}")
                try:
                    process.kill()
                except:
                    pass
            
            return {
                "success": False,
                "error": f"Processing timed out after {timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Error running ScreenArc CLI: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_npm_script(
        self,
        input_video: str,
        output_video: str,
        preset: str,
        metadata_path: Optional[str],
        **options
    ) -> Dict:
        """Run ScreenArc via npm script"""
        # Convert to absolute paths to avoid path resolution issues
        input_video_abs = str(Path(input_video).resolve())
        output_video_abs = str(Path(output_video).resolve())
        
        # Ensure output directory exists
        Path(output_video_abs).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "npm", "run", SCREENARC_NPM_SCRIPT, "--",
            "-i", input_video_abs,
            "-o", output_video_abs,
            "-p", preset
        ]
        
        if metadata_path:
            cmd.extend(["-m", metadata_path])
        
        try:
            logger.info(f"Running ScreenArc via npm: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=str(self.screenarc_root),
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_video_abs,
                    "processing_time": elapsed
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_process_screenarc(
        self,
        input_dir: str,
        output_dir: str,
        preset: str = "cinematic"
    ) -> List[Dict]:
        """
        Batch process videos with ScreenArc
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            preset: Preset name
            
        Returns:
            List of processing results
        """
        if not self.node_available:
            return []
        
        cmd = [
            "node",
            str(self.cli_path),
            "batch",
            "-i", input_dir,
            "-o", output_dir,
            "-p", preset,
            "--json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.screenarc_root),
                capture_output=True,
                text=True,
                timeout=7200  # 2 hours for batch
            )
            
            if result.returncode == 0:
                # Parse JSON results
                results_file = os.path.join(output_dir, "batch-results.json")
                if os.path.exists(results_file):
                    with open(results_file, 'r') as f:
                        return json.load(f)
            
            return []
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return []
    
    def check_screenarc_setup(self) -> Dict:
        """
        Check ScreenArc setup and dependencies
        
        Returns:
            Setup status dictionary
        """
        status = {
            "screenarc_exists": self.screenarc_root.exists(),
            "cli_exists": self.cli_path.exists() if self.screenarc_root.exists() else False,
            "node_available": self.node_available,
            "npm_available": self.npm_available,
            "ready": False
        }
        
        if status["screenarc_exists"] and status["node_available"]:
            # Check if dependencies are installed
            package_json = self.screenarc_root / "package.json"
            node_modules = self.screenarc_root / "node_modules"
            
            status["dependencies_installed"] = node_modules.exists()
            status["ready"] = status["cli_exists"] or (status["npm_available"] and package_json.exists())
        
        return status

# Global wrapper instance
screenarc_wrapper = ScreenArcWrapper()
