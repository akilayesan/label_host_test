import fitz
import cv2
import numpy as np
import os


def remove_red_color(image):
    """
    Remove red-colored pixels by converting them to white.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    cleaned = image.copy()
    cleaned[mask > 0] = [255, 255, 255]

    return cleaned


def detect_labels(pdf_path, output_folder, min_area=20000):
    """
    Detect label regions from PDF and save them as images.
    Returns list of saved image paths.
    """

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    label_count = 0
    saved_images = []

    for page_number in range(len(doc)):

        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=300)

        img = np.frombuffer(pix.samples, dtype=np.uint8)
        img = img.reshape(pix.height, pix.width, pix.n)

        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

        # Remove red first
        img_no_red = remove_red_color(img)
        original = img_no_red.copy()

        gray = cv2.cvtColor(img_no_red, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            closed,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:

            area = cv2.contourArea(cnt)
            if area < min_area:
                continue

            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) == 4:

                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)

                if 1.2 < aspect_ratio < 3.5:

                    cropped = original[y:y+h, x:x+w]

                    label_count += 1

                    output_path = os.path.join(
                        output_folder,
                        f"label_{label_count}.png"
                    )

                    cv2.imwrite(output_path, cropped)
                    saved_images.append(output_path)

    return saved_images