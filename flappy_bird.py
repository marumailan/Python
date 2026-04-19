"""Flappy Bird clone — single-file, stdlib only (tkinter).

Run:  python3 flappy_bird.py
Controls:  SPACE or mouse click to flap / start / restart.  Esc quits.

Sprites are generated procedurally at startup using PhotoImage.put(), so the
script is fully self-contained — no external image files required.
"""

import random
import tkinter as tk

# --- Configuration ----------------------------------------------------------

WIDTH = 400
HEIGHT = 600
GROUND_HEIGHT = 80
SKY_HEIGHT = HEIGHT - GROUND_HEIGHT

GRAVITY = 0.45
FLAP_VELOCITY = -7.5
MAX_FALL_SPEED = 11.0
TILT_UP = -25
TILT_DOWN = 70

PIPE_WIDTH = 56
PIPE_GAP = 150
PIPE_SPEED = 3
PIPE_SPAWN_FRAMES = 90  # ~1.5 s at 60 FPS
MIN_PIPE_HEIGHT = 50

GROUND_SPEED = PIPE_SPEED
TICK_MS = 16  # ~60 FPS

SKY_COLOR = "#70c5ce"
GROUND_TOP_COLOR = "#ded895"
GROUND_BOTTOM_COLOR = "#c0a060"

STATE_READY = "ready"
STATE_PLAYING = "playing"
STATE_OVER = "over"


# --- Sprite helpers ---------------------------------------------------------


def fill_rect(img, x1, y1, x2, y2, color):
    """Fill an axis-aligned rectangle in a PhotoImage."""
    if x2 <= x1 or y2 <= y1:
        return
    img.put(color, to=(x1, y1, x2, y2))


def make_bird_image(wing_state):
    """Procedurally draw a chunky pixel-art bird sprite.

    wing_state: 0 = wing up, 1 = wing mid, 2 = wing down.
    Returns a PhotoImage sized 34x24.
    """
    w, h = 34, 24
    img = tk.PhotoImage(width=w, height=h)

    YELLOW = "#fad749"
    YELLOW_DK = "#e0a020"
    WHITE = "#ffffff"
    BLACK = "#000000"
    ORANGE = "#f08020"
    ORANGE_LT = "#fac070"
    ORANGE_DK = "#c06010"
    WING_LT = "#ffffff"
    WING_MD = "#dddddd"
    WING_DK = "#a0a0a0"

    # Body fill (rounded rectangle approximation)
    fill_rect(img, 4, 6, 30, 20, YELLOW)
    fill_rect(img, 6, 4, 28, 22, YELLOW)
    fill_rect(img, 2, 8, 32, 18, YELLOW)

    # Belly
    fill_rect(img, 8, 14, 24, 20, WHITE)
    fill_rect(img, 10, 20, 22, 22, WHITE)

    # Body outline (top, bottom, left curve)
    fill_rect(img, 6, 3, 28, 4, BLACK)
    fill_rect(img, 4, 4, 6, 6, BLACK)
    fill_rect(img, 2, 6, 4, 8, BLACK)
    fill_rect(img, 0, 8, 2, 18, BLACK)
    fill_rect(img, 2, 18, 4, 20, BLACK)
    fill_rect(img, 4, 20, 6, 22, BLACK)
    fill_rect(img, 6, 22, 26, 23, BLACK)
    fill_rect(img, 26, 20, 28, 22, BLACK)
    fill_rect(img, 28, 18, 30, 20, BLACK)

    # Right side outline (above/below beak)
    fill_rect(img, 28, 6, 30, 11, BLACK)
    fill_rect(img, 28, 17, 30, 18, BLACK)

    # Eye
    fill_rect(img, 21, 6, 28, 13, WHITE)
    fill_rect(img, 22, 5, 27, 14, WHITE)
    fill_rect(img, 20, 7, 21, 12, BLACK)  # left eye outline
    fill_rect(img, 21, 5, 28, 6, BLACK)
    fill_rect(img, 21, 13, 28, 14, BLACK)
    fill_rect(img, 28, 7, 29, 12, BLACK)
    fill_rect(img, 24, 8, 27, 12, BLACK)  # pupil

    # Beak
    fill_rect(img, 28, 11, 34, 17, ORANGE)
    fill_rect(img, 30, 10, 33, 11, ORANGE_LT)
    fill_rect(img, 30, 17, 33, 18, ORANGE_DK)
    fill_rect(img, 33, 12, 34, 16, ORANGE_DK)
    # Beak outline
    fill_rect(img, 28, 10, 30, 11, BLACK)
    fill_rect(img, 28, 17, 30, 18, BLACK)
    fill_rect(img, 33, 11, 34, 12, BLACK)
    fill_rect(img, 33, 16, 34, 17, BLACK)

    # Wing — three frames at different vertical positions / shapes.
    if wing_state == 0:  # wing up (raised)
        fill_rect(img, 6, 7, 18, 11, WING_LT)
        fill_rect(img, 8, 6, 16, 7, WING_LT)
        fill_rect(img, 6, 6, 8, 7, BLACK)
        fill_rect(img, 16, 6, 18, 7, BLACK)
        fill_rect(img, 4, 7, 6, 11, BLACK)
        fill_rect(img, 18, 7, 20, 11, BLACK)
        fill_rect(img, 6, 11, 18, 12, BLACK)
    elif wing_state == 1:  # wing mid (level)
        fill_rect(img, 6, 11, 18, 15, WING_MD)
        fill_rect(img, 8, 10, 16, 11, WING_MD)
        fill_rect(img, 6, 10, 8, 11, BLACK)
        fill_rect(img, 16, 10, 18, 11, BLACK)
        fill_rect(img, 4, 11, 6, 15, BLACK)
        fill_rect(img, 18, 11, 20, 15, BLACK)
        fill_rect(img, 6, 15, 18, 16, BLACK)
    else:  # wing down (lowered)
        fill_rect(img, 6, 14, 18, 18, WING_DK)
        fill_rect(img, 8, 13, 16, 14, WING_DK)
        fill_rect(img, 6, 13, 8, 14, BLACK)
        fill_rect(img, 16, 13, 18, 14, BLACK)
        fill_rect(img, 4, 14, 6, 18, BLACK)
        fill_rect(img, 18, 14, 20, 18, BLACK)
        fill_rect(img, 6, 18, 18, 19, BLACK)

    return img


def make_pipe_image(height, cap_at_top):
    """Generate a pipe sprite of given pixel height with a cap on top or bottom."""
    w = PIPE_WIDTH
    h = max(height, 30)
    img = tk.PhotoImage(width=w, height=h)

    GREEN = "#73bf2e"
    GREEN_LT = "#a8e060"
    GREEN_DK = "#558c1e"
    OUTLINE = "#3d4d14"

    # Body
    fill_rect(img, 0, 0, w, h, GREEN)
    fill_rect(img, 4, 0, 14, h, GREEN_LT)         # left highlight
    fill_rect(img, w - 14, 0, w - 4, h, GREEN_DK)  # right shadow
    fill_rect(img, 0, 0, 2, h, OUTLINE)
    fill_rect(img, w - 2, 0, w, h, OUTLINE)

    # Cap region
    cap_h = 26
    if cap_at_top:
        y0, y1 = 0, cap_h
    else:
        y0, y1 = h - cap_h, h

    fill_rect(img, 0, y0, w, y1, GREEN)
    fill_rect(img, 4, y0, 16, y1, GREEN_LT)
    fill_rect(img, w - 16, y0, w - 4, y1, GREEN_DK)
    fill_rect(img, 0, y0, 4, y1, OUTLINE)
    fill_rect(img, w - 4, y0, w, y1, OUTLINE)
    fill_rect(img, 0, y0, w, y0 + 2, OUTLINE)
    fill_rect(img, 0, y1 - 2, w, y1, OUTLINE)

    return img


def make_ground_image():
    """Make a wide repeating ground tile (a band of textured strips)."""
    w = WIDTH * 2  # wide enough to scroll
    h = GROUND_HEIGHT
    img = tk.PhotoImage(width=w, height=h)

    fill_rect(img, 0, 0, w, h, GROUND_TOP_COLOR)
    fill_rect(img, 0, 0, w, 4, "#3d4d14")          # dark top edge
    fill_rect(img, 0, 4, w, 12, "#73bf2e")         # green grass band
    fill_rect(img, 0, 12, w, 16, "#a8e060")        # grass highlight
    fill_rect(img, 0, 16, w, h, GROUND_TOP_COLOR)
    fill_rect(img, 0, h - 20, w, h, GROUND_BOTTOM_COLOR)

    # Diagonal stripes for motion cue
    stripe_color = "#c2a060"
    for x in range(0, w, 24):
        fill_rect(img, x, h - 18, x + 12, h - 4, stripe_color)
    return img


def make_cloud_image():
    img = tk.PhotoImage(width=60, height=22)
    WHITE = "#ffffff"
    SHADOW = "#dde9eb"
    fill_rect(img, 8, 8, 52, 18, WHITE)
    fill_rect(img, 14, 4, 30, 8, WHITE)
    fill_rect(img, 26, 2, 44, 6, WHITE)
    fill_rect(img, 36, 6, 50, 10, WHITE)
    fill_rect(img, 8, 16, 52, 18, SHADOW)
    return img


# --- Game -------------------------------------------------------------------


class FlappyBird:
    def __init__(self, root):
        self.root = root
        root.title("Flappy Bird")
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=SKY_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Pre-generate sprites once. Keep references to prevent GC.
        self.bird_sprites = [make_bird_image(i) for i in range(3)]
        self.ground_sprite = make_ground_image()
        self.cloud_sprite = make_cloud_image()
        self.pipe_image_cache = {}  # (height, cap_at_top) -> PhotoImage

        # State variables (initialised in reset()).
        self.state = STATE_READY
        self.bird_y = 0.0
        self.bird_vy = 0.0
        self.frame = 0
        self.score = 0
        self.high_score = 0
        self.pipes = []  # list of dicts: top_id, bot_id, x, gap_y, scored
        self.spawn_timer = 0
        self.bird_id = None
        self.ground_ids = []
        self.cloud_ids = []
        self.score_text_id = None
        self.overlay_ids = []

        # Static decorations
        self._draw_clouds()
        self._draw_ground()

        # Bindings
        root.bind("<space>", self.flap)
        root.bind("<Button-1>", self.flap)
        root.bind("<Escape>", lambda _e: root.destroy())

        self.reset()
        self._tick()

    # -- Setup helpers --

    def _draw_clouds(self):
        positions = [(60, 80), (220, 130), (320, 60), (140, 200)]
        for x, y in positions:
            cid = self.canvas.create_image(x, y, image=self.cloud_sprite, anchor="nw")
            self.cloud_ids.append(cid)

    def _draw_ground(self):
        # Two ground tiles side-by-side for seamless scrolling.
        g1 = self.canvas.create_image(0, SKY_HEIGHT, image=self.ground_sprite, anchor="nw")
        g2 = self.canvas.create_image(WIDTH * 2, SKY_HEIGHT, image=self.ground_sprite, anchor="nw")
        self.ground_ids = [g1, g2]

    def _get_pipe_image(self, height, cap_at_top):
        key = (height, cap_at_top)
        if key not in self.pipe_image_cache:
            self.pipe_image_cache[key] = make_pipe_image(height, cap_at_top)
        return self.pipe_image_cache[key]

    # -- Game state --

    def reset(self):
        # Remove pipes and overlay
        for pipe in self.pipes:
            self.canvas.delete(pipe["top_id"])
            self.canvas.delete(pipe["bot_id"])
        self.pipes = []

        if self.bird_id is not None:
            self.canvas.delete(self.bird_id)
        if self.score_text_id is not None:
            self.canvas.delete(self.score_text_id)
        for oid in self.overlay_ids:
            self.canvas.delete(oid)
        self.overlay_ids = []

        self.bird_y = HEIGHT * 0.4
        self.bird_vy = 0.0
        self.frame = 0
        self.score = 0
        self.spawn_timer = PIPE_SPAWN_FRAMES  # spawn first pipe quickly after start

        self.bird_id = self.canvas.create_image(
            80, self.bird_y, image=self.bird_sprites[1], anchor="center"
        )

        self.score_text_id = self.canvas.create_text(
            WIDTH // 2,
            60,
            text="0",
            fill="white",
            font=("Helvetica", 36, "bold"),
        )
        # Hide score until playing
        self.canvas.itemconfig(self.score_text_id, state="hidden")

        self.state = STATE_READY
        self._show_overlay_ready()

    def _show_overlay_ready(self):
        title = self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 - 60,
            text="Flappy Bird",
            fill="white",
            font=("Helvetica", 32, "bold"),
        )
        sub = self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 + 20,
            text="Press SPACE or click to flap",
            fill="white",
            font=("Helvetica", 14),
        )
        self.overlay_ids.extend([title, sub])

    def _show_overlay_game_over(self):
        # Semi-opaque banner via solid rect (tkinter has no alpha for canvas items)
        banner = self.canvas.create_rectangle(
            40, HEIGHT // 2 - 90, WIDTH - 40, HEIGHT // 2 + 90,
            fill="#000000", outline="white", width=2,
        )
        title = self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 50,
            text="GAME OVER", fill="#ff6060",
            font=("Helvetica", 28, "bold"),
        )
        score = self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 10,
            text=f"Score: {self.score}", fill="white",
            font=("Helvetica", 18, "bold"),
        )
        best = self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 20,
            text=f"Best: {self.high_score}", fill="white",
            font=("Helvetica", 14),
        )
        retry = self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 60,
            text="Press SPACE to play again", fill="#ffe080",
            font=("Helvetica", 12),
        )
        self.overlay_ids.extend([banner, title, score, best, retry])

    def _clear_overlay(self):
        for oid in self.overlay_ids:
            self.canvas.delete(oid)
        self.overlay_ids = []

    # -- Input --

    def flap(self, _event=None):
        if self.state == STATE_READY:
            self.state = STATE_PLAYING
            self._clear_overlay()
            self.canvas.itemconfig(self.score_text_id, state="normal")
            self.bird_vy = FLAP_VELOCITY
        elif self.state == STATE_PLAYING:
            self.bird_vy = FLAP_VELOCITY
        elif self.state == STATE_OVER:
            self.reset()

    # -- Pipes --

    def spawn_pipe(self):
        # Random gap-y position.
        min_top = MIN_PIPE_HEIGHT
        max_top = SKY_HEIGHT - MIN_PIPE_HEIGHT - PIPE_GAP
        top_h = random.randint(min_top, max(min_top + 1, max_top))
        bot_h = SKY_HEIGHT - top_h - PIPE_GAP

        top_img = self._get_pipe_image(top_h, cap_at_top=False)
        bot_img = self._get_pipe_image(bot_h, cap_at_top=True)

        x = WIDTH + PIPE_WIDTH // 2
        top_id = self.canvas.create_image(x, 0, image=top_img, anchor="n")
        bot_id = self.canvas.create_image(x, SKY_HEIGHT, image=bot_img, anchor="s")

        self.pipes.append({
            "top_id": top_id,
            "bot_id": bot_id,
            "x": float(x),
            "top_h": top_h,
            "bot_h": bot_h,
            "scored": False,
        })

    # -- Main loop --

    def _tick(self):
        try:
            if self.state == STATE_PLAYING:
                self._update_playing()
            elif self.state == STATE_READY:
                # Idle: just bob the bird gently
                self._idle_bob()
            # STATE_OVER: nothing moves.

            # Always animate wing while window is alive
            self.frame += 1
            if self.state != STATE_OVER:
                wing = (self.frame // 5) % 3
                self.canvas.itemconfig(self.bird_id, image=self.bird_sprites[wing])
        except tk.TclError:
            return  # Window was closed.

        self.root.after(TICK_MS, self._tick)

    def _idle_bob(self):
        # Sinusoidal-ish bob using frame counter
        offset = 4.0 * ((self.frame % 60) / 60.0 - 0.5)
        self.canvas.coords(self.bird_id, 80, self.bird_y + offset * 2)

    def _update_playing(self):
        # Bird physics
        self.bird_vy = min(self.bird_vy + GRAVITY, MAX_FALL_SPEED)
        self.bird_y += self.bird_vy
        self.canvas.coords(self.bird_id, 80, self.bird_y)

        # Scroll ground
        for gid in self.ground_ids:
            self.canvas.move(gid, -GROUND_SPEED, 0)
        # Wrap ground tiles
        for gid in self.ground_ids:
            x = self.canvas.coords(gid)[0]
            if x <= -WIDTH * 2:
                # Move it to the right of the other tile
                others = [self.canvas.coords(o)[0] for o in self.ground_ids if o != gid]
                self.canvas.coords(gid, max(others) + WIDTH * 2, SKY_HEIGHT)

        # Pipe spawning
        self.spawn_timer += 1
        if self.spawn_timer >= PIPE_SPAWN_FRAMES:
            self.spawn_timer = 0
            self.spawn_pipe()

        # Move pipes; cull off-screen; score when bird passes
        for pipe in list(self.pipes):
            pipe["x"] -= PIPE_SPEED
            self.canvas.move(pipe["top_id"], -PIPE_SPEED, 0)
            self.canvas.move(pipe["bot_id"], -PIPE_SPEED, 0)

            if not pipe["scored"] and pipe["x"] + PIPE_WIDTH // 2 < 80:
                pipe["scored"] = True
                self.score += 1
                self.canvas.itemconfig(self.score_text_id, text=str(self.score))

            if pipe["x"] < -PIPE_WIDTH:
                self.canvas.delete(pipe["top_id"])
                self.canvas.delete(pipe["bot_id"])
                self.pipes.remove(pipe)

        # Collisions
        if self._check_collision():
            self._game_over()

    def _check_collision(self):
        # Bird AABB (smaller than sprite for forgiving feel)
        bx1, by1 = 80 - 12, self.bird_y - 9
        bx2, by2 = 80 + 12, self.bird_y + 9

        # Ground / ceiling
        if by2 >= SKY_HEIGHT:
            return True
        if by1 <= 0:
            self.bird_y = 9
            self.bird_vy = 0
            return False  # don't end on ceiling, just clamp

        for pipe in self.pipes:
            px1 = pipe["x"] - PIPE_WIDTH // 2
            px2 = pipe["x"] + PIPE_WIDTH // 2
            if px2 < bx1 or px1 > bx2:
                continue
            top_y2 = pipe["top_h"]
            bot_y1 = SKY_HEIGHT - pipe["bot_h"]
            if by1 < top_y2 or by2 > bot_y1:
                return True
        return False

    def _game_over(self):
        self.state = STATE_OVER
        if self.score > self.high_score:
            self.high_score = self.score
        self._show_overlay_game_over()


def main():
    root = tk.Tk()
    FlappyBird(root)
    root.mainloop()


if __name__ == "__main__":
    main()
