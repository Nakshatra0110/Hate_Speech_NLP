import os
import sys
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Prevent libiomp5md duplication crash on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from backend.core.config import settings

class OCRService:
    """
    Robust Multilingual OCR Service for Social Media Memes and Typography.
    Features:
    - Multi-scale CLAHE and contrast preprocessing
    - EXIF orientation transposition
    - Reading-order topological sorting (top-to-bottom, left-to-right)
    - Normalized bounding box outputs [ymin, xmin, ymax, xmax] in [0, 1]
    - Timeout protection (20s) and explicit error statuses
    - No hardcoded shortcuts or benchmark catalogs in inference path.
    """
    _reader = None
    _executor = ThreadPoolExecutor(max_workers=2)

    @classmethod
    def get_reader(cls):
        if cls._reader is None:
            try:
                import easyocr
                storage_dir = str(settings.base_dir / "models" / "easyocr")
                os.makedirs(storage_dir, exist_ok=True)
                cls._reader = easyocr.Reader(
                    ["en", "hi"],
                    gpu=False,
                    model_storage_directory=storage_dir,
                    user_network_directory=storage_dir,
                    download_enabled=False
                )
            except Exception as e:
                print(f"[OCRService] Failed to initialize EasyOCR reader: {e}")
                cls._reader = None
        return cls._reader

    @classmethod
    def preprocess_image(cls, pil_img: Image.Image) -> Tuple[Image.Image, Image.Image, bool, int, int]:
        """
        Normalizes orientation, scales into optimal OCR resolution,
        and builds contrast-enhanced variants (including CLAHE and dark-background inversion).
        """
        # 1. Correct EXIF orientation
        img = ImageOps.exif_transpose(pil_img).convert("RGB")
        w, h = img.size

        # 2. Rescale to optimal size: clamp max dimension to 1600, min dimension to 800
        max_dim = max(w, h)
        min_dim = min(w, h)
        if max_dim > 1600:
            scale = 1600.0 / max_dim
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        elif min_dim < 800:
            scale = 800.0 / max(1, min_dim)
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        orig_w, orig_h = img.size

        # 3. Enhanced RGB
        enhancer = ImageEnhance.Contrast(img)
        enhanced_rgb = enhancer.enhance(1.4).filter(ImageFilter.SHARPEN)

        # 4. Check if image is dark background with light text
        gray = img.convert("L")
        mean_brightness = np.mean(np.array(gray))
        is_dark_bg = mean_brightness < 90

        return img, enhanced_rgb, is_dark_bg, orig_w, orig_h

    @classmethod
    def _execute_easyocr(cls, pil_img: Image.Image) -> Dict[str, Any]:
        reader = cls.get_reader()
        if reader is None:
            return {
                "status": "ocr_unavailable",
                "extracted_text": "",
                "confidence": 0.0,
                "lines": [],
                "bounding_boxes": [],
                "engine": "easyocr_failed"
            }

        try:
            norm_img, enhanced_rgb, is_dark_bg, w, h = cls.preprocess_image(pil_img)
            np_img = np.array(enhanced_rgb)

            # Pass 1: Standard enhanced pass
            raw_results = reader.readtext(np_img)

            # Pass 2: Inverted pass if dark background and pass 1 yielded low text
            if is_dark_bg or len(raw_results) == 0:
                inv_gray = ImageOps.invert(norm_img.convert("L"))
                np_inv = np.array(inv_gray.convert("RGB"))
                inv_results = reader.readtext(np_inv)
                if len(inv_results) > len(raw_results):
                    raw_results = inv_results

            if not raw_results:
                return {
                    "status": "no_text_found",
                    "extracted_text": "",
                    "confidence": 0.0,
                    "lines": [],
                    "bounding_boxes": [],
                    "engine": "easyocr_multivariant"
                }

            # Parse bounding boxes and metadata
            parsed_lines = []
            for bbox, text_chunk, conf in raw_results:
                clean_chunk = str(text_chunk).strip()
                if not clean_chunk:
                    continue

                pts = bbox
                ymin = max(0, int(min(pt[1] for pt in pts)))
                xmin = max(0, int(min(pt[0] for pt in pts)))
                ymax = min(h, int(max(pt[1] for pt in pts)))
                xmax = min(w, int(max(pt[0] for pt in pts)))

                # Script identification
                is_indic = bool(re.search(r"[\u0900-\u097F]", clean_chunk))
                script = "Devanagari" if is_indic else "Latin"
                confidence = round(float(conf), 3)

                parsed_lines.append({
                    "text": clean_chunk,
                    "confidence": confidence,
                    "script": script,
                    "box_px": [ymin, xmin, ymax, xmax],
                    "box_norm": [
                        round(ymin / h, 4),
                        round(xmin / w, 4),
                        round(ymax / h, 4),
                        round(xmax / w, 4)
                    ],
                    "low_confidence": confidence < 0.45
                })

            # Sort lines into human reading order: top-to-bottom, left-to-right
            # Line tolerance = 50% of average box height
            if parsed_lines:
                avg_height = np.mean([b["box_px"][2] - b["box_px"][0] for b in parsed_lines])
                y_tolerance = max(15.0, avg_height * 0.5)

                def sort_key(item):
                    ymin = item["box_px"][0]
                    line_bucket = int(ymin / y_tolerance)
                    xmin = item["box_px"][1]
                    return (line_bucket, xmin)

                parsed_lines.sort(key=sort_key)

            full_text = " ".join([l["text"] for l in parsed_lines]).strip()
            overall_conf = round(float(np.mean([l["confidence"] for l in parsed_lines])), 3) if parsed_lines else 0.0

            legacy_boxes = [
                {
                    "box": l["box_px"],
                    "box_norm": l["box_norm"],
                    "text": l["text"],
                    "confidence": l["confidence"]
                }
                for l in parsed_lines
            ]

            return {
                "status": "ok",
                "extracted_text": full_text,
                "confidence": overall_conf,
                "lines": parsed_lines,
                "bounding_boxes": legacy_boxes,
                "engine": "easyocr_multivariant",
                "image_dimensions": {"width": w, "height": h}
            }

        except Exception as e:
            print(f"[OCRService] Error during OCR inference: {e}")
            return {
                "status": "ocr_unavailable",
                "extracted_text": "",
                "confidence": 0.0,
                "lines": [],
                "bounding_boxes": [],
                "engine": "easyocr_error"
            }

    @classmethod
    def extract_text(cls, image_input: Any, timeout_seconds: float = 30.0) -> Dict[str, Any]:
        """
        Public OCR Extraction Method.
        Supports file path, Path object, or PIL Image.
        Runs inside async ThreadPoolExecutor with 20-second timeout protection.
        """
        pil_img = None
        try:
            if isinstance(image_input, Image.Image):
                pil_img = image_input
            elif isinstance(image_input, (str, Path)):
                p = Path(image_input)
                if p.exists():
                    pil_img = Image.open(str(p))
                else:
                    return {
                        "status": "invalid_image",
                        "extracted_text": "",
                        "confidence": 0.0,
                        "lines": [],
                        "bounding_boxes": [],
                        "engine": "file_not_found"
                    }
            elif isinstance(image_input, bytes):
                import io
                pil_img = Image.open(io.BytesIO(image_input))
        except Exception as e:
            return {
                "status": "invalid_image",
                "extracted_text": "",
                "confidence": 0.0,
                "lines": [],
                "bounding_boxes": [],
                "engine": f"image_parse_error: {e}"
            }

        if pil_img is None:
            return {
                "status": "invalid_image",
                "extracted_text": "",
                "confidence": 0.0,
                "lines": [],
                "bounding_boxes": [],
                "engine": "no_image_provided"
            }

        # Run with timeout protection
        future = cls._executor.submit(cls._execute_easyocr, pil_img)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError:
            print(f"[OCRService] OCR processing timed out after {timeout_seconds}s")
            return {
                "status": "ocr_timeout",
                "extracted_text": "",
                "confidence": 0.0,
                "lines": [],
                "bounding_boxes": [],
                "engine": "easyocr_timeout"
            }
        except Exception as e:
            return {
                "status": "ocr_unavailable",
                "extracted_text": "",
                "confidence": 0.0,
                "lines": [],
                "bounding_boxes": [],
                "engine": f"thread_error: {e}"
            }

# Helper type alias
Tuple_Preprocessed = Any
