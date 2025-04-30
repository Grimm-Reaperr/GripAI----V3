import math

# === CONFIGURATION ===
REFERENCE_CM = 20
BOX_WIDTH_PX = 225
PIXELS_PER_CM = BOX_WIDTH_PX / REFERENCE_CM
SAVE_PATH = "assets/output.jpg"
DIST_THRESHOLD_CM = 1.6
COUNTDOWN_SECONDS = 2.0

# === ADJUSTMENT FACTORS ===
WIDTH_ADJUSTMENT_LINE = 0.70   # in inches 0.20
HEIGHT_ADJUSTMENT_LINE = 0.40  # in inches

# === UTILITY FUNCTIONS ===

def calculate_distance(px1, py1, px2, py2):
    return math.hypot(px2 - px1, py2 - py1)

def pixels_to_cm(px, pixels_per_cm=PIXELS_PER_CM):
    return px / pixels_per_cm

def cm_to_inches(cm):
    return cm / 2.54

def find_weight_category(width_in, height_in):
    area = width_in * height_in
    return math.ceil(area)
