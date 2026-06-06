import pygame, sys, math, random

pygame.init()
W, H = 680, 480
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18)
big_font = pygame.font.SysFont("monospace", 32)

BRICK_COLS, BRICK_ROWS = 13, 6
BRICK_W, BRICK_H, BRICK_PAD = 46, 16, 4
BRICK_OFF_X = (W - (BRICK_COLS * (BRICK_W + BRICK_PAD) - BRICK_PAD)) // 2
BRICK_OFF_Y = 60
COLORS = [(248,113,113),(251,146,60),(251,191,36),(74,222,128),(96,165,250),(167,139,250)]

def make_bricks():
    bricks = []
    for r in range(BRICK_ROWS):
        for c in range(BRICK_COLS):
            x = BRICK_OFF_X + c * (BRICK_W + BRICK_PAD)
            y = BRICK_OFF_Y + r * (BRICK_H + BRICK_PAD)
            hp = 2 if r < 2 else 1
            bricks.append({"rect": pygame.Rect(x, y, BRICK_W, BRICK_H), "color": COLORS[r], "hp": hp})
    return bricks

def reset(lives=3, score=0, level=1):
    paddle = pygame.Rect(W//2 - 50, H - 40, 100, 12)
    spd = 4 + level * 0.4
    angle = random.choice([-1, 1])
    ball = {"rect": pygame.Rect(W//2 - 8, H - 60, 16, 16), "vx": spd * angle, "vy": -spd}
    return paddle, ball, make_bricks(), score, lives, "ready"

particles = []
level = 1
paddle, ball, bricks, score, lives, state = reset()

def spawn_particles(x, y, color):
    for _ in range(10):
        a = random.uniform(0, math.pi * 2)
        s = random.uniform(1, 4)
        particles.append({"x": x, "y": y, "vx": math.cos(a)*s, "vy": math.sin(a)*s,
                          "life": 1.0, "color": color, "size": random.randint(2, 4)})

running = True
while running:
    clock.tick(60)
    mx = pygame.mouse.get_pos()[0]
    paddle.x = max(0, min(W - paddle.width, mx - paddle.width // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if state == "ready": state = "playing"
                elif state == "dead": level=1; paddle,ball,bricks,score,lives,state = reset()
                elif state == "win": paddle,ball,bricks,score,lives,state = reset(lives,score,level)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: paddle.x = max(0, paddle.x - 6)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: paddle.x = min(W - paddle.width, paddle.x + 6)

    if state == "ready":
        ball["rect"].centerx = paddle.centerx
        ball["rect"].y = paddle.y - 17

    if state == "playing":
        ball["rect"].x += int(ball["vx"])
        ball["rect"].y += int(ball["vy"])

        if ball["rect"].left < 0: ball["vx"] = abs(ball["vx"]); ball["rect"].left = 0
        if ball["rect"].right > W: ball["vx"] = -abs(ball["vx"]); ball["rect"].right = W
        if ball["rect"].top < 0: ball["vy"] = abs(ball["vy"]); ball["rect"].top = 0

        if ball["rect"].colliderect(paddle) and ball["vy"] > 0:
            hit = (ball["rect"].centerx - paddle.centerx) / (paddle.width / 2)
            spd = math.sqrt(ball["vx"]**2 + ball["vy"]**2)
            ball["vx"] = hit * 6
            ball["vy"] = -abs(ball["vy"])
            s = math.sqrt(ball["vx"]**2 + ball["vy"]**2)
            ball["vx"] = ball["vx"] / s * spd
            ball["vy"] = ball["vy"] / s * spd
            ball["rect"].bottom = paddle.top

        if ball["rect"].top > H + 20:
            lives -= 1
            if lives <= 0: state = "dead"
            else: paddle,ball,bricks,_,_,state = reset(lives, score, level); state="ready"

        for b in bricks:
            if b["hp"] <= 0: continue
            if ball["rect"].colliderect(b["rect"]):
                ol = ball["rect"].right - b["rect"].left
                or_ = b["rect"].right - ball["rect"].left
                ot = ball["rect"].bottom - b["rect"].top
                ob = b["rect"].bottom - ball["rect"].top
                if min(ol, or_) < min(ot, ob): ball["vx"] *= -1
                else: ball["vy"] *= -1
                b["hp"] -= 1
                score += 10 if b["hp"] == 0 else 5
                if b["hp"] == 0: spawn_particles(b["rect"].centerx, b["rect"].centery, b["color"])
                break

        if all(b["hp"] <= 0 for b in bricks):
            level += 1; state = "win"

        for p in particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.1; p["life"] -= 0.05
        particles = [p for p in particles if p["life"] > 0]

    screen.fill((13, 17, 23))

    for b in bricks:
        if b["hp"] <= 0: continue
        c = b["color"] if b["hp"] == 1 else tuple(min(255, x+60) for x in b["color"])
        pygame.draw.rect(screen, c, b["rect"], border_radius=3)
        pygame.draw.rect(screen, (255,255,255,30), b["rect"], 1, border_radius=3)

    pygame.draw.rect(screen, (148, 163, 184), paddle, border_radius=6)
    pygame.draw.circle(screen, (255, 255, 255), ball["rect"].center, 8)

    for p in particles:
        alpha_surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*p["color"], int(p["life"]*255)),
                          (p["size"], p["size"]), p["size"])
        screen.blit(alpha_surf, (int(p["x"]) - p["size"], int(p["y"]) - p["size"]))

    screen.blit(font.render(f"Score: {score}   Lives: {'●'*lives}   Level: {level}", True, (255,255,255)), (10, 20))

    if state == "ready":
        msg = font.render("Press SPACE to launch!", True, (200, 200, 200))
        screen.blit(msg, (W//2 - msg.get_width()//2, H//2 + 60))
    elif state == "dead":
        msg = big_font.render(f"Game Over! Score: {score}", True, (248,113,113))
        sub = font.render("Press SPACE to restart", True, (180,180,180))
        screen.blit(msg, (W//2 - msg.get_width()//2, H//2 - 20))
        screen.blit(sub, (W//2 - sub.get_width()//2, H//2 + 20))
    elif state == "win":
        msg = big_font.render(f"Level {level}!", True, (74,222,128))
        sub = font.render("Press SPACE to continue", True, (180,180,180))
        screen.blit(msg, (W//2 - msg.get_width()//2, H//2 - 20))
        screen.blit(sub, (W//2 - sub.get_width()//2, H//2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()