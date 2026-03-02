"""
Orchestration - Pipeline Manager
Central coordination for batch pipelines
"""

import uuid
import asyncio
from typing import Dict
import logging
import time
import os
from pathlib import Path
from orchestration.state_machine import create_state_machine, get_state_machine, BatchState

logger = logging.getLogger(__name__)

# Job status tracking
_job_statuses: Dict[str, Dict] = {}

async def start_batch_pipeline(payload: Dict) -> str:
    """
    Start a batch content pipeline
    
    Args:
        payload: Batch request payload
        
    Returns:
        Job ID
    """
    job_id = str(uuid.uuid4())
    
    logger.info(f"Starting batch pipeline: {job_id}")
    
    # Initialize job status
    _job_statuses[job_id] = {
        "status": "queued",
        "progress": 0,
        "created_at": asyncio.get_event_loop().time(),
        "payload": payload
    }
    
    # Create state machine
    state_machine = create_state_machine(job_id)
    
    # Run pipeline asynchronously
    asyncio.create_task(run_pipeline(job_id, payload, state_machine))
    
    return job_id

async def get_job_status(job_id: str) -> Dict:
    """Get status of a job"""
    return _job_statuses.get(job_id, {
        "job_id": job_id,
        "status": "not_found",
        "error": "Job not found"
    })

async def run_pipeline(job_id: str, payload: Dict, state_machine=None):
    """Run the full pipeline"""
    if not state_machine:
        state_machine = get_state_machine(job_id) or create_state_machine(job_id)
    
    try:
        _job_statuses[job_id]["status"] = "processing"
        _job_statuses[job_id]["progress"] = 0
        
        # 1. Generate ideas
        state_machine.transition_to(BatchState.HOOK_GENERATED)
        _job_statuses[job_id]["progress"] = 10
        from services.topic_engine.idea_generator import generate_ideas_async
        ideas = await generate_ideas_async(count=1)
        topic = ideas[0] if ideas else payload.get("topic", "Default topic")
        _job_statuses[job_id]["topic"] = topic
        
        # 2. Generate hooks (with ML if available)
        state_machine.transition_to(BatchState.HOOK_GENERATED)
        _job_statuses[job_id]["progress"] = 20
        from services.hook_engine.hook_scorer import generate_hooks_for_topic
        hooks = await generate_hooks_for_topic(topic, count=5, use_ml=True)
        _job_statuses[job_id]["hooks"] = len(hooks)
        
        # Use RL agent to select best strategy
        from models.reinforcement_learning import viral_rl_agent
        from models.training_data_collector import training_data_collector
        
        # Build state vector for RL
        hook_vector = training_data_collector._build_hook_feature_vector(
            hooks[0].get("hook", ""),
            hooks[0].get("angle", "speed")
        )
        retention_vector = training_data_collector._build_retention_feature_vector((None,) * 8, 60.0)
        topic_vector = training_data_collector._build_topic_feature_vector(payload.get("cluster", "rebuild_tools"))
        
        rl_state = hook_vector.to_list() + retention_vector.to_list() + topic_vector.to_list()
        rl_strategy = viral_rl_agent.select_content_strategy(rl_state)
        _job_statuses[job_id]["rl_strategy"] = rl_strategy
        
        # 3. Record video (if input provided, use it; otherwise record)
        state_machine.transition_to(BatchState.RECORDED)
        _job_statuses[job_id]["progress"] = 30
        if payload.get("input_video"):
            from pathlib import Path
            video_path = str(Path(payload["input_video"]).resolve())  # Convert to absolute path
        else:
            from services.recording_service.screen_capture import capture_screen_async
            duration = payload.get("duration", 60)
            video_path = await capture_screen_async(duration=duration)
        _job_statuses[job_id]["video_path"] = video_path
        
        # 4. Optimize retention
        state_machine.transition_to(BatchState.OPTIMIZED)
        _job_statuses[job_id]["progress"] = 50
        from services.recording_service.video_processor import optimize_for_retention
        from services.retention_optimizer.silence_detector import detect_silence
        from services.retention_optimizer.pause_trimmer import trim_pauses
        
        # Detect and trim silence
        try:
            silence_periods = detect_silence(video_path)
            if silence_periods:
                video_path = trim_pauses(video_path, silence_periods)
        except Exception as e:
            logger.warning(f"Silence detection failed: {e}, continuing")
        
        # Optimize with ScreenArc (includes zoom injection if transcript available)
        # Check if video is already optimized/exported to avoid adding multiple _optimized suffixes
        from pathlib import Path
        video_path_obj = Path(video_path)
        if "_optimized" in video_path_obj.stem or "exports" in str(video_path_obj).lower():
            # Already optimized/exported, use a different naming scheme
            optimized_path = str(video_path_obj.parent / f"{video_path_obj.stem}_vcos_processed{video_path_obj.suffix}")
        else:
            optimized_path = video_path.replace(".mp4", "_optimized.mp4")
        
        # Validate video file before processing (with wait for file to be fully written)
        import cv2
        import time
        def validate_video_file(video_path: str, max_wait_seconds: int = 10) -> bool:
            """Validate video file, waiting for it to be fully written"""
            if not os.path.exists(video_path):
                return False
            
            # Wait for file size to stabilize (file is being written)
            start_time = time.time()
            last_size = 0
            stable_count = 0
            
            while time.time() - start_time < max_wait_seconds:
                try:
                    current_size = os.path.getsize(video_path)
                    if current_size == 0:
                        time.sleep(0.5)
                        continue
                    
                    if current_size == last_size:
                        stable_count += 1
                        if stable_count >= 3:  # Stable for 1.5 seconds
                            break
                    else:
                        stable_count = 0
                        last_size = current_size
                    
                    time.sleep(0.5)
                except OSError:
                    time.sleep(0.5)
                    continue
            
            if os.path.getsize(video_path) == 0:
                return False
            
            # Try ffprobe first (more reliable for MP4)
            try:
                import subprocess
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except:
                pass  # Fall back to OpenCV
            
            # Fallback: OpenCV validation
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return False
                ret, _ = cap.read()
                cap.release()
                return ret
            except:
                return False
        
        if not validate_video_file(video_path, max_wait_seconds=15):
            raise ValueError(f"Input video file is invalid or corrupted (or still being written): {video_path}")
        
        # Try to optimize, but don't block forever - aggressive timeout
        # The optimize_for_retention function now has built-in 45s timeout
        try:
            video_path = optimize_for_retention(video_path, optimized_path, transcript=None)
            # Validate optimized video
            if not validate_video_file(video_path):
                logger.warning(f"Optimized video is invalid, using original")
                video_path = str(Path(input_video).resolve())
            _job_statuses[job_id]["optimized_video"] = video_path
            logger.info(f"Optimization completed: {video_path}")
        except Exception as e:
            logger.warning(f"Optimization failed or timed out: {e}, using original video for variants")
            # Use original video if optimization fails - but validate it first!
            original_path = str(Path(input_video).resolve())
            if not validate_video_file(original_path):
                raise ValueError(f"Both optimized and original video files are invalid. Cannot continue pipeline.")
            video_path = original_path
            optimized_path = video_path
            _job_statuses[job_id]["optimized_video"] = video_path
            _job_statuses[job_id]["optimization_warning"] = str(e)
            logger.info(f"Continuing pipeline with original video: {video_path}")
        
        # 5. Generate variants (with pruning)
        state_machine.transition_to(BatchState.VARIANTS_CREATED)
        _job_statuses[job_id]["progress"] = 70
        from services.variant_generator.variant_registry import register_variant
        from services.variant_generator.pacing_variator import generate_speed_variants
        from services.variant_generator.variant_pruner import variant_pruner
        from models.training_data_collector import training_data_collector
        
        num_variants = payload.get("num_variants", 20)
        
        # Generate variant configurations (2x for pruning)
        variant_configs = []
        for i in range(num_variants * 2):
            hook_data = hooks[i % len(hooks)]
            
            # Build feature vectors for prediction
            hook_vector = training_data_collector._build_hook_feature_vector(
                hook_data.get("hook", ""),
                hook_data.get("angle", "speed")
            )
            retention_vector = training_data_collector._build_retention_feature_vector((None,) * 8, 60.0)
            topic_vector = training_data_collector._build_topic_feature_vector(payload.get("cluster", "rebuild_tools"))
            
            variant_config = {
                "id": i + 1,
                "hook_features": hook_vector.to_list(),
                "retention_features": retention_vector.to_list(),
                "topic_features": topic_vector.to_list(),
                "hook_angle": hook_data.get("angle", "speed"),
                "pacing_speed": 1.0 + (i % 5) * 0.03,  # 1.0 to 1.12
                "zoom_density": ["subtle", "moderate", "aggressive", "no_zoom"][i % 4]  # Include no_zoom option
            }
            variant_configs.append(variant_config)
        
        # Prune variants based on predicted performance
        pruned_variants = variant_pruner.prune_variants(variant_configs)
        _job_statuses[job_id]["variants_pruned"] = len(variant_configs) - len(pruned_variants)
        
        # Generate actual variant videos from pruned configs
        variant_paths = []
        from pathlib import Path
        from services.variant_generator.video_transformer import VideoTransformer
        from services.variant_generator.zoom_pattern_variator import generate_zoom_schedule
        from services.variant_generator.subtitle_style_variator import SUBTITLE_STYLES
        
        transformer = VideoTransformer()
        
        # Get video info for zoom scheduling
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 60.0
            video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
        except Exception as e:
            logger.warning(f"Failed to get video info: {e}, using defaults")
            video_duration = 60.0
            video_width = 1920
            video_height = 1080
        
        # Save variants to variants directory, not raw directory
        from shared.config.settings import settings
        variants_dir = Path(settings.VARIANTS_DIR)
        variants_dir.mkdir(parents=True, exist_ok=True)
        
        for variant in pruned_variants[:num_variants]:  # Keep top N
            variant_path = str(variants_dir / f"{Path(video_path).stem}_variant_{variant['id']}.mp4")
            
            try:
                # Build transformation configuration
                transformations = {}
                
                # 1. Speed adjustment
                if variant.get("pacing_speed", 1.0) != 1.0:
                    transformations["speed"] = variant["pacing_speed"]
                
                # 2. Zoom pattern
                zoom_density = variant.get("zoom_density", "moderate")
                zoom_schedule = generate_zoom_schedule(video_duration, zoom_density)
                
                # Convert zoom schedule to zoom regions
                zoom_regions = []
                for zoom_event in zoom_schedule:
                    zoom_width = int(video_width / zoom_event["intensity"])
                    zoom_height = int(video_height / zoom_event["intensity"])
                    zoom_x = (video_width - zoom_width) // 2
                    zoom_y = (video_height - zoom_height) // 2
                    
                    zoom_regions.append({
                        "timestamp": zoom_event["timestamp"],
                        "x": zoom_x,
                        "y": zoom_y,
                        "width": zoom_width,
                        "height": zoom_height,
                        "duration": zoom_event["duration"],
                        "intensity": zoom_event["intensity"]
                    })
                
                if zoom_regions:
                    transformations["zoom_regions"] = zoom_regions
                
                # 3. Subtitles (if transcript available)
                # For now, skip subtitles as we don't have transcript in pipeline
                # TODO: Add transcript extraction/processing
                
                # Apply all transformations
                if transformations:
                    logger.info(f"Applying transformations to variant {variant['id']}: {list(transformations.keys())}")
                    try:
                        transformer.apply_all_transformations(
                            video_path,
                            transformations,
                            variant_path
                        )
                        # Validate output file
                        if not os.path.exists(variant_path) or os.path.getsize(variant_path) == 0:
                            raise RuntimeError(f"Variant file was not created or is empty: {variant_path}")
                    except Exception as e:
                        logger.error(f"Failed to create variant {variant['id']}: {e}")
                        # Try to copy original as fallback
                        try:
                            import shutil
                            Path(variant_path).parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(video_path, variant_path)
                            logger.warning(f"Used original video as fallback for variant {variant['id']}")
                        except Exception as copy_error:
                            logger.error(f"Failed to create fallback variant {variant['id']}: {copy_error}")
                            continue  # Skip this variant
                else:
                    # No transformations, just copy
                    import shutil
                    Path(variant_path).parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(video_path, variant_path)
                    except Exception as e:
                        logger.error(f"Failed to copy variant {variant['id']}: {e}")
                        continue  # Skip this variant
                
                logger.info(f"Created variant: {variant_path}")
                
                # Register the variant
                register_variant(
                    f"base_{job_id}",
                    {
                        "pacing_speed": variant["pacing_speed"],
                        "hook_type": variant["hook_angle"],
                        "zoom_density": variant["zoom_density"]
                    },
                    variant_path
                )
                variant_paths.append(variant_path)
                
            except Exception as e:
                logger.error(f"Failed to create variant {variant['id']}: {e}", exc_info=True)
                continue
        
        _job_statuses[job_id]["variants"] = len(variant_paths)
        
        # 6. Export and publish (if requested)
        _job_statuses[job_id]["progress"] = 90
        platforms = payload.get("platforms", [])
        if platforms and variant_paths:
            state_machine.transition_to(BatchState.PUBLISHED)
            from services.export_service.encoder import encode_for_platform
            encoded = []
            for platform in platforms:
                for variant_path in variant_paths[:3]:  # Limit exports
                    # Check if variant file actually exists before encoding
                    if not Path(variant_path).exists():
                        logger.warning(f"Variant file does not exist: {variant_path}, skipping encoding")
                        continue
                    try:
                        encoded_path = encode_for_platform(variant_path, platform)
                        encoded.append(encoded_path)
                    except Exception as e:
                        logger.error(f"Failed to encode {variant_path} for {platform}: {e}")
                        # Continue with other variants instead of failing entire pipeline
                        continue
            _job_statuses[job_id]["encoded"] = len(encoded)
        else:
            # No platforms specified or no variants - just mark as completed
            logger.info(f"No platforms specified or no variants created, skipping encoding")
        
        _job_statuses[job_id]["progress"] = 100
        state_machine.transition_to(BatchState.COMPLETED)
        _job_statuses[job_id]["status"] = "completed"
        _job_statuses[job_id]["completed_at"] = time.time()
        logger.info(f"Pipeline completed: {job_id}")
        
    except Exception as e:
        import traceback
        _job_statuses[job_id]["status"] = "failed"
        _job_statuses[job_id]["error"] = str(e)
        _job_statuses[job_id]["error_traceback"] = traceback.format_exc()
        _job_statuses[job_id]["failed_at"] = time.time()
        if state_machine:
            state_machine.fail(str(e))
        logger.error(f"Pipeline failed {job_id}: {e}\n{traceback.format_exc()}")
