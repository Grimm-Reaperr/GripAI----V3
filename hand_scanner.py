import cv2
import math
import time
import mediapipe as mp
from utils import (
    BOX_WIDTH_PX,
    REFERENCE_CM,
    PIXELS_PER_CM,
    SAVE_PATH,
    COUNTDOWN_SECONDS,
    DIST_THRESHOLD_CM,
    WIDTH_ADJUSTMENT_LINE,
    HEIGHT_ADJUSTMENT_LINE,
    calculate_distance,
    pixels_to_cm,
    cm_to_inches,
    find_weight_category,
)

def run_measurement(save_path=SAVE_PATH):
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    countdown_start = None
    counting_down = False

    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.8) as hands:
        while True:
            success, frame = cap.read()
            if not success:
                break

            h, w = frame.shape[:2]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            # Draw guide box on screen
            box_x1 = w // 2 - BOX_WIDTH_PX // 2
            box_y1 = h // 2 - BOX_WIDTH_PX // 2
            box_x2 = w // 2 + BOX_WIDTH_PX // 2
            box_y2 = h // 2 + BOX_WIDTH_PX // 2
            cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 255, 255), 2)
            cv2.putText(frame, f"Fit wrist in {REFERENCE_CM}cm box", (box_x1, box_y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            def is_hand_inside_box(landmarks):
                points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                margin = int(BOX_WIDTH_PX * 0.05)
                return (
                    min(x_coords) > box_x1 + margin and max(x_coords) < box_x2 - margin and
                    min(y_coords) > box_y1 + margin and max(y_coords) < box_y2 - margin
                )

            hand_centered = False

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]

                if is_hand_inside_box(hand_landmarks):
                    hand_centered = True

                    def get_px(pt):
                        lm = hand_landmarks.landmark[pt]
                        return int(lm.x * w), int(lm.y * h)

                    # Measure width and height
                    width_px = calculate_distance(*get_px(mp_hands.HandLandmark.INDEX_FINGER_MCP),
                                                  *get_px(mp_hands.HandLandmark.PINKY_MCP))
                    height_px = calculate_distance(*get_px(mp_hands.HandLandmark.WRIST),
                                                   *get_px(mp_hands.HandLandmark.MIDDLE_FINGER_TIP))

                    width_cm = pixels_to_cm(width_px)
                    height_cm = pixels_to_cm(height_px)

                    width_in = cm_to_inches(width_cm) + WIDTH_ADJUSTMENT_LINE
                    height_in = cm_to_inches(height_cm) + HEIGHT_ADJUSTMENT_LINE

                    # Draw lines
                    cv2.line(frame, get_px(mp_hands.HandLandmark.INDEX_FINGER_MCP),
                             get_px(mp_hands.HandLandmark.PINKY_MCP), (0, 255, 0), 2)
                    cv2.line(frame, get_px(mp_hands.HandLandmark.WRIST),
                             get_px(mp_hands.HandLandmark.MIDDLE_FINGER_TIP), (255, 0, 0), 2)

                    # Display width and height
                    cv2.putText(frame, f"W: {width_in:.2f} in", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, f"H: {height_in:.2f} in", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                    # Calculate proximity to box top/bottom
                    x12, y12 = get_px(mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
                    x0, y0 = get_px(mp_hands.HandLandmark.WRIST)
                    dist_top_cm = pixels_to_cm(abs(y12 - box_y1))
                    dist_bottom_cm = pixels_to_cm(abs(box_y2 - y0))

                    # Draw distance lines
                    cv2.line(frame, (x12, y12), (x12, box_y1), (255, 255, 0), 2)
                    cv2.line(frame, (x0, y0), (x0, box_y2), (255, 0, 255), 2)

                    # Show distances
                    cv2.putText(frame, f"Top: {dist_top_cm:.2f} cm", (30, 170),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    cv2.putText(frame, f"Bottom: {dist_bottom_cm:.2f} cm", (30, 200),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

                    # Start countdown if hand is close enough
                    if dist_top_cm <= DIST_THRESHOLD_CM and dist_bottom_cm <= DIST_THRESHOLD_CM:
                        if not counting_down:
                            countdown_start = time.time()
                            counting_down = True
                        else:
                            elapsed = time.time() - countdown_start
                            remaining = int(COUNTDOWN_SECONDS - elapsed)
                            if remaining > 0:
                                cv2.putText(frame, f"Capturing in {remaining}s...", (30, 130),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                            else:
                                weight_category = find_weight_category(width_in, height_in)
                                print(f"🖐️ Hand size score: {weight_category}")
                                cv2.imwrite(save_path, frame)
                                print(f"✅ Auto-captured and saved to {save_path}")
                                break
                    else:
                        counting_down = False
                        cv2.putText(frame, "Move hand forward...", (30, 130),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            else:
                counting_down = False  # reset if no hand

            cv2.imshow("Hand Measurement", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == ord('c') and hand_centered:
                weight_category = find_weight_category(width_in, height_in)
                print(f"🖐️ Hand size score: {weight_category}")
                cv2.imwrite(save_path, frame)
                print(f"✅ Captured and saved to {save_path}")
                break

    cap.release()
    cv2.destroyAllWindows()
