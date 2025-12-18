import cv2
import numpy as np
from PIL import Image

def detect_split_points(pil_image):
    """
    Analyze a page image to detect signatures, stamps, or other markers 
    that indicate a potential document boundary
    
    Args:
        pil_image: PIL Image object of the PDF page
        
    Returns:
        Boolean indicating if this page might be a good split point
    """
    # Convert PIL image to OpenCV format (numpy array)
    img_np = np.array(pil_image)
    
    # Convert to grayscale if the image is in color
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np.copy()
    
    # Preprocessing: enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Apply threshold to segment ink from background
    _, thresh = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Signature and stamp detection strategies:
    has_signature = False
    
    # 1. Look for handwritten signature patterns
    # - Detect connected components that might be signatures
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size and shape attributes typical of signatures
    signature_candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:  # Skip very small noise
            continue
            
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # Typical signatures have these attributes:
        # - Medium to large area
        # - Width greater than height (aspect ratio > 1)
        # - Located in the bottom half of the page
        if area > 1000 and 1 < aspect_ratio < 8 and y > gray.shape[0] * 0.5:
            signature_candidates.append(contour)
    
    # 2. Check for stamp-like circular patterns
    circles = cv2.HoughCircles(
        enhanced, 
        cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=20, 
        param1=50, 
        param2=30, 
        minRadius=20, 
        maxRadius=100
    )
    
    # Decision rules for suggesting a split
    if len(signature_candidates) >= 1:
        # Found potential signature(s)
        has_signature = True
    
    if circles is not None and len(circles) > 0:
        # Found potential stamp(s)
        has_signature = True
    
    # Look for textual indicators in the bottom portion of the page
    bottom_region = thresh[int(thresh.shape[0] * 0.7):, :]
    text_density = np.sum(bottom_region) / (bottom_region.shape[0] * bottom_region.shape[1])
    
    # High text density in bottom portion can indicate signature blocks, dates, etc.
    if text_density > 0.03:  # Threshold determined experimentally
        has_signature = True
    
    return has_signature
