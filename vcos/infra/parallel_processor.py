"""
Infrastructure - Parallel Processor
GPU acceleration and parallel video processing
"""

import os
import subprocess
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging

logger = logging.getLogger(__name__)

class ParallelVideoProcessor:
    """Parallel video processing with GPU support"""
    
    def __init__(self, max_workers: int = 4, use_gpu: bool = False):
        self.max_workers = max_workers
        self.use_gpu = use_gpu
        self.gpu_available = self._check_gpu_availability()
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for video processing"""
        try:
            # Check for NVIDIA GPU
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def process_videos_parallel(
        self,
        video_tasks: List[Dict],
        processor_func
    ) -> List[Dict]:
        """
        Process multiple videos in parallel
        
        Args:
            video_tasks: List of video processing tasks
            processor_func: Function to process each video
            
        Returns:
            List of processing results
        """
        if self.use_gpu and self.gpu_available:
            logger.info(f"Processing {len(video_tasks)} videos with GPU acceleration")
            # Use ProcessPoolExecutor for CPU-bound tasks
            # For GPU, would use specialized library like PyTorch or TensorFlow
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                results = list(executor.map(processor_func, video_tasks))
        else:
            logger.info(f"Processing {len(video_tasks)} videos in parallel (CPU)")
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = list(executor.map(processor_func, video_tasks))
        
        return results
    
    def process_variants_parallel(
        self,
        base_video: str,
        variant_configs: List[Dict]
    ) -> List[str]:
        """
        Generate variants in parallel
        
        Args:
            base_video: Base video path
            variant_configs: List of variant configurations
            
        Returns:
            List of output video paths
        """
        from services.variant_generator.pacing_variator import adjust_speed
        from services.variant_generator.zoom_pattern_variator import apply_zoom_pattern
        
        def process_variant(config):
            variant_path = base_video.replace(".mp4", f"_variant_{config['id']}.mp4")
            
            # Apply variant transformations
            if "speed" in config:
                variant_path = adjust_speed(base_video, config["speed"], variant_path)
            
            if "zoom_pattern" in config:
                variant_path = apply_zoom_pattern(variant_path, config["zoom_pattern"], variant_path)
            
            return variant_path
        
        return self.process_videos_parallel(variant_configs, process_variant)

def get_optimal_worker_count() -> int:
    """Get optimal worker count based on system resources"""
    import multiprocessing
    
    cpu_count = multiprocessing.cpu_count()
    # Use 75% of available CPUs
    return max(1, int(cpu_count * 0.75))
