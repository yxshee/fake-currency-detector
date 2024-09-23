
---

# **Fake Currency Detection System Using Machine Learning**



This project focuses on developing an automated system for detecting counterfeit Indian currency notes using advanced image processing and machine learning techniques. It targets common users and small businesses that lack access to expensive currency validation equipment typically found in banks and corporate environments. The system is capable of detecting fake 500 and 2000 rupee notes by analyzing various security features of the currency.

## Technologies and Libraries Used:

- **Programming Language**: Python

- **Development Environment**: Jupyter Notebook

- **Libraries**:

  - **OpenCV**: For image processing and computer vision tasks
  - **Tkinter**: For creating the graphical user interface (GUI)
  - **SSIM (Structural Similarity Index)**: For image comparison
  - **ORB (Oriented FAST and Rotated BRIEF)**: For feature extraction and matching
  - **NumPy**: For numerical computation
  - **Matplotlib**: For visualization and analysis
  - **Scikit-image**: For SSIM-based similarity scoring

## Key Features:

1. **Image Acquisition**: Captures images of currency notes using digital cameras or scanners.

2. **Pre-processing**: Image resizing, Gaussian blurring, and grayscale conversion are performed to prepare the image for analysis.

   ```python
   
   def preprocess_image(image):
       # Resize image to standard size
       resized_image = cv2.resize(image, (800, 400))
       
       # Convert to grayscale
       gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
       
       # Apply Gaussian blur to reduce noise
       blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
       
       return blurred_image
   ```
   
3. **Feature Detection and Matching**:

    - **Security Thread**: Uses ORB algorithm for detecting key currency features like the security thread. <br>
   ```python
   
   # ORB feature detection
   orb = cv2.ORB_create()
   keypoints1, descriptors1 = orb.detectAndCompute(image1, None)
   keypoints2, descriptors2 = orb.detectAndCompute(image2, None)
   
   # BruteForce Matcher
   bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
   matches = bf.match(descriptors1, descriptors2)
   matches = sorted(matches, key = lambda x:x.distance)
   ```
   
   - **Bleed Lines**: Detects the presence and count of angular bleed lines in the 500 and 2000 rupee notes.
     
     

   ```python
   
   def count_bleed_lines(image):
       # Apply binary threshold
       _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
       
       # Find contours
       contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
       # Count contours that match the expected shape of bleed lines
       bleed_line_count = 0
       for cnt in contours:
           if valid_bleed_line(cnt):
               bleed_line_count += 1
       
       return bleed_line_count
   ```
   
   - **Number Panel**: Verifies the number of characters in the serial number panel on the note.
     
     
5. **Image Analysis**: Compares extracted features using SSIM to determine whether the currency is real or fake.

    ```python
    
   from skimage.metrics import structural_similarity as ssim
   
   def compare_images(imageA, imageB):
       # Compute SSIM between two images
       score, _ = ssim(imageA, imageB, full=True)
       return score
   ```

6. **GUI**: A user-friendly graphical interface built using Tkinter, enabling users to upload images of currency notes and receive instant validation results.
   
   ```python
   import tkinter as tk
   from tkinter import filedialog
   from PIL import ImageTk, Image
   
   def open_image():
       file_path = filedialog.askopenfilename()
       img = Image.open(file_path)
       img = img.resize((400, 200), Image.ANTIALIAS)
       img = ImageTk.PhotoImage(img)
       panel.config(image=img)
       panel.image = img
   ```

## Methodology:

- **Image Processing Algorithms**:
  
  - The system follows a structured process for image acquisition, preprocessing, feature extraction, and analysis using a combination of ORB and SSIM techniques.
  - **Algorithm 1**: Validates security features like latent images, watermarks, security threads, and Mahatma Gandhi's portrait.
  - **Algorithm 2**: Checks the bleed lines on both sides of the currency notes.
  - **Algorithm 3**: Verifies the number panel.

## Results:

- **Accuracy**:
  
  - Real Notes: 79% accuracy based on testing of 500 and 2000 rupee notes.
  - Fake Notes: 83% accuracy based on testing of fake notes from the same denominations.
  
- **Performance**:
  
  - Processing time is approximately 5 seconds per note when only final results are displayed, making it a quick and efficient solution for counterfeit detection.

## Conclusion:

The **Fake Currency Detection System** provides an effective, user-friendly, and accurate method for detecting counterfeit currency. By leveraging advanced image processing techniques, the system is capable of validating important security features on Indian currency notes and providing results with high accuracy. This project offers a practical solution for addressing the rising issue of currency counterfeiting in everyday transactions.

---

