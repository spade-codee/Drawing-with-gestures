import cv2
import mediapipe as mp
import pygame
import time
import math
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Gesture Drawing App")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# Drawing variables
drawing = False
erasing = False
stamping = False
last_pos = None
color = (255, 0, 0)
colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 255)]
canvas = pygame.Surface((800, 600))
canvas.fill((9, 0, 9))
color_change_cooldown = 0
thick_brush = False
brush_type = "solid"

# Preview states
tool_preview = None
tool_preview_start = 0
brush_preview = None
brush_preview_start = 0

# Webcam setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Couldn't open webcam")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Star stamp
def draw_star(surface, color, center, size):
    x, y = center
    points = []
    for i in range(10):
        angle = math.radians(i * 36)
        radius = size if i % 2 == 0 else size / 2
        points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
    pygame.draw.polygon(surface, color, points)

# Brush draw styles
def draw_line(surface, color, start, end, thickness):
    if brush_type == "solid":
        pygame.draw.line(surface, color, start, end, thickness)
    elif brush_type == "dashed":
        dash_len = 10
        dist = math.hypot(end[0]-start[0], end[1]-start[1])
        for i in range(0, int(dist), dash_len*2):
            dx = start[0] + (end[0]-start[0]) * (i/dist)
            dy = start[1] + (end[1]-start[1]) * (i/dist)
            dx2 = start[0] + (end[0]-start[0]) * ((i+dash_len)/dist)
            dy2 = start[1] + (end[1]-start[1]) * ((i+dash_len)/dist)
            pygame.draw.line(surface, color, (dx, dy), (dx2, dy2), thickness)
    elif brush_type == "spray":
        for _ in range(30):
            offset = (random.randint(-10, 10), random.randint(-10, 10))
            pygame.draw.circle(surface, color, (end[0]+offset[0], end[1]+offset[1]), 1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                cap.release()
                pygame.quit()
                exit()
            elif event.key == pygame.K_c:
                canvas.fill((0, 0, 0))
            elif event.key == pygame.K_s:
                filename = f"drawing_{int(time.time())}.png"
                pygame.image.save(canvas, filename)

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if color_change_cooldown > 0:
        color_change_cooldown -= 1

    current_time = time.time()
    screen.blit(canvas, (0, 0))

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Landmark positions
        lm = hand_landmarks.landmark
        ix, iy = int(lm[8].x * 800), int(lm[8].y * 600)
        mx, my = int(lm[12].x * 800), int(lm[12].y * 600)
        rx, ry = int(lm[16].x * 800), int(lm[16].y * 600)
        px, py = int(lm[20].x * 800), int(lm[20].y * 600)
        tx, ty = int(lm[4].x * 800), int(lm[4].y * 600)
        wx, wy = int(lm[0].x * 800), int(lm[0].y * 600)

        # Thumb rotation gesture for color
        thumb_angle = math.degrees(math.atan2(ty - wy, tx - wx))
        if color_change_cooldown == 0 and abs(thumb_angle) > 120:
            color = colors[(colors.index(color) + 1) % len(colors)]
            color_change_cooldown = 30

        # Shape tool: Circle (index + middle up)
        if lm[8].y < lm[6].y and lm[12].y < lm[10].y and lm[16].y > lm[14].y:
            if tool_preview != "circle":
                tool_preview = "circle"
                tool_preview_start = current_time
            elif current_time - tool_preview_start >= 1:
                pygame.draw.circle(canvas, color, (ix, iy), 30)
                tool_preview = None
        # Shape tool: Rectangle (index + pinky up)
        elif lm[8].y < lm[6].y and lm[20].y < lm[18].y and lm[12].y > lm[10].y:
            if tool_preview != "rect":
                tool_preview = "rect"
                tool_preview_start = current_time
            elif current_time - tool_preview_start >= 1:
                pygame.draw.rect(canvas, color, (ix - 30, iy - 20, 60, 40))
                tool_preview = None
        # Brush type: Peace (index+middle up, ring+pinky down)
        elif lm[8].y < lm[6].y and lm[12].y < lm[10].y and lm[16].y > lm[14].y and lm[20].y > lm[18].y:
            if brush_preview != "dashed":
                brush_preview = "dashed"
                brush_preview_start = current_time
            elif current_time - brush_preview_start >= 1:
                brush_type = "dashed"
                brush_preview = None
        # Brush type: Rock (index+pinky up, others down)
        elif lm[8].y < lm[6].y and lm[20].y < lm[18].y and lm[12].y > lm[10].y:
            if brush_preview != "spray":
                brush_preview = "spray"
                brush_preview_start = current_time
            elif current_time - brush_preview_start >= 1:
                brush_type = "spray"
                brush_preview = None
        # Drawing
        elif lm[8].y < lm[6].y and lm[12].y > lm[10].y:
            if last_pos:
                draw_line(canvas, color, last_pos, (ix, iy), 5 if not thick_brush else 10)
            last_pos = (ix, iy)
            drawing = True
        else:
            last_pos = None
            drawing = False
    else:
        last_pos = None
        drawing = False

    # Draw preview labels
    if tool_preview:
        label = font.render(f"HOLD: {tool_preview.upper()}", True, (255, 255, 255))
        screen.blit(label, (600, 20))
    if brush_preview:
        label = font.render(f"BRUSH: {brush_preview.upper()}", True, (255, 255, 255))
        screen.blit(label, (600, 50))

    pygame.draw.rect(screen, color, (10, 10, 30, 30))
    pygame.display.flip()
    cv2.imshow("Webcam Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
