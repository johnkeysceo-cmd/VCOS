"""
Infrastructure - GPU Acceleration
GPU-accelerated video processing and ML inference
"""

import os
import logging

logger = logging.getLogger(__name__)

def check_gpu_available() -> bool:
    """Check if GPU is available"""
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_gpu_memory_info() -> Dict:
    """Get GPU memory information"""
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.free", "--format=csv,noheader"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines:
                total, free = lines[0].split(', ')
                return {
                    "total_mb": int(total.replace(" MiB", "")),
                    "free_mb": int(free.replace(" MiB", "")),
                    "available": True
                }
    except Exception as e:
        logger.warning(f"Error getting GPU info: {e}")
    
    return {"available": False}

def configure_ffmpeg_gpu(use_gpu: bool = True) -> List[str]:
    """
    Configure FFmpeg for GPU acceleration
    
    Args:
        use_gpu: Whether to use GPU
        
    Returns:
        FFmpeg encoding arguments
    """
    if not use_gpu or not check_gpu_available():
        # CPU encoding
        return [
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23"
        ]
    
    # GPU encoding (NVIDIA NVENC)
    return [
        "-c:v", "h264_nvenc",
        "-preset", "p4",  # Fast preset
        "-cq", "23",
        "-b:v", "5M"
    ]

def configure_ml_inference_gpu(use_gpu: bool = True) -> Dict:
    """
    Configure ML inference for GPU
    
    Args:
        use_gpu: Whether to use GPU
        
    Returns:
        Inference configuration
    """
    config = {
        "device": "cpu",
        "batch_size": 32
    }
    
    if use_gpu and check_gpu_available():
        try:
            import torch
            if torch.cuda.is_available():
                config["device"] = "cuda"
                config["batch_size"] = 128  # Larger batches on GPU
                logger.info("ML inference configured for GPU")
        except ImportError:
            logger.warning("PyTorch not installed, using CPU")
    
    return config
