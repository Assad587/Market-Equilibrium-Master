import pygame
import sys
import numpy as np
import random
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("市场均衡大师")

# Colors
BACKGROUND = (20, 30, 48)
PANEL_COLOR = (30, 40, 60)
ACCENT_COLOR = (0, 150, 255)
SECONDARY_COLOR = (255, 105, 180)
WHITE = (240, 240, 245)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
BLUE = (30, 180, 255)
GREEN = (50, 220, 120)
GRAY = (100, 110, 130)
YELLOW = (255, 215, 0)
DARK_GRAY = (30, 35, 45)
LIGHT_GRAY = (60, 70, 90)
SHADOW = (20, 25, 35)
HIGHLIGHT = (0, 200, 255)
BUTTON_COLOR = (50, 180, 255)
BUTTON_HOVER = (70, 200, 255)
BUTTON_DISABLED = (100, 110, 130)

# Fonts
font_small = pygame.font.SysFont("simhei", 18)
font = pygame.font.SysFont("simhei", 22, bold=True)
font_large = pygame.font.SysFont("simhei", 36, bold=True)
font_title = pygame.font.SysFont("simhei", 28, bold=True)
font_ui = pygame.font.SysFont("simhei", 20)

# Game variables
price = 20
inventory = 100
profit = 0
rounds = 0
max_rounds = 10
slider_x = 300
dragging = False
points = 0
event_message = "没有事件"
demand_shift = 0
supply_shift = 0
timer = 60  # 延长回合时间
last_time = pygame.time.get_ticks() / 1000
goal = "最小化库存"
restart_button = pygame.Rect(800, 620, 160, 60)
start_button = pygame.Rect(400, 300, 200, 60)
help_button = pygame.Rect(400, 380, 200, 60)
submit_button = pygame.Rect(750, 520, 200, 50)  # 提交按钮位置调整
game_state = "start"  # "start", "playing", "game_over", "round_transition"
help_open = False
history = []
animation_timer = 0
particles = []
achievements = []
difficulty = "中等"  # 简单, 中等, 困难
round_transition_time = 0
current_round_result = None
next_round_event = None
next_round_goal = None
supply_factor = 3.0
demand_factor = 2.0
base_supply = 10
base_demand = 100
round_completed = False  # 标记回合是否已完成
help_scroll = 0  # 帮助界面滚动位置
max_help_scroll = 0  # 最大滚动范围

# Economic functions
def demand(price, shift=0):
    return max(0, base_demand - demand_factor * price + shift)

def supply(price, shift=0):
    return max(0, base_supply + supply_factor * price + shift)

# Random events
def apply_random_event():
    events = [
        ("干旱减少供应", 0, -random.randint(15, 30)),
        ("节日增加需求", random.randint(15, 30), 0),
        ("新供应商进入", 0, random.randint(10, 20)),
        ("经济衰退", -random.randint(10, 20), 0),
        ("技术进步", 0, random.randint(5, 15)),
        ("消费者偏好改变", random.randint(5, 15), 0),
        ("原材料涨价", 0, -random.randint(10, 20)),
        ("政府补贴", 0, random.randint(5, 15)),
        ("没有事件", 0, 0)
    ]
    
    # Adjust event probability based on difficulty
    weights = [1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8, 0.8, 0.5]
    if difficulty == "简单":
        weights = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
    elif difficulty == "困难":
        weights = [1.5, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 0.3]
            
    return random.choices(events, weights=weights, k=1)[0]

# Draw supply and demand curves
def draw_curves(screen, price):
    # 缩小图表区域以避免重叠
    graph_width, graph_height = 550, 400
    graph_x, graph_y = 50, 50
    
    # Graph background
    pygame.draw.rect(screen, PANEL_COLOR, (graph_x, graph_y, graph_width, graph_height), 0, 10)
    pygame.draw.rect(screen, ACCENT_COLOR, (graph_x, graph_y, graph_width, graph_height), 3, 10)
    
    # 调整网格密度
    for i in range(0, graph_width+1, 50):
        pygame.draw.line(screen, LIGHT_GRAY, (graph_x + i, graph_y), (graph_x + i, graph_y + graph_height), 1)
    for i in range(0, graph_height+1, 40):
        pygame.draw.line(screen, LIGHT_GRAY, (graph_x, graph_y + i), (graph_x + graph_width, graph_y + i), 1)
    # Draw axes with padding
    pygame.draw.line(screen, ACCENT_COLOR, (graph_x+10, graph_y+10), (graph_x+10, graph_y+graph_height-10), 3)  # Y-axis
    pygame.draw.line(screen, ACCENT_COLOR, (graph_x+10, graph_y+graph_height-10), (graph_x+graph_width-10, graph_y+graph_height-10), 3)  # X-axis
    
    # Draw axis markers with adjusted positions
    for i in range(0, 11):
        y_pos = graph_y + graph_height - 20 - i * 36
        if y_pos > graph_y + 10:
            pygame.draw.line(screen, ACCENT_COLOR, (graph_x+5, y_pos), (graph_x+15, y_pos), 2)
            screen.blit(font_small.render(str(i*5), True, WHITE), (graph_x-15, y_pos-8))
        
    for i in range(0, 11):
        x_pos = graph_x + 20 + i * 50
        if x_pos < graph_x + graph_width - 10:
            pygame.draw.line(screen, ACCENT_COLOR, (x_pos, graph_y+graph_height-15), (x_pos, graph_y+graph_height-5), 2)
            screen.blit(font_small.render(str(i*15), True, WHITE), (x_pos-10, graph_y+graph_height+5))
    
    # Draw title and labels
    screen.blit(font_title.render("供给与需求曲线", True, WHITE), (graph_x+graph_width//2-70, graph_y-25))
    screen.blit(font.render("价格 ($)", True, WHITE), (graph_x-20, graph_y+graph_height//2-70))
    screen.blit(font.render("数量", True, WHITE), (graph_x+graph_width//2-20, graph_y+graph_height+15))
    
    # 调整曲线绘制范围，避免超出边界
    demand_points = []
    supply_points = []
    # 需求曲线
    for q in range(0, 151, 5):
        p_val = (base_demand - q + demand_shift) / demand_factor
        if p_val < 0 or p_val > 50:
            continue
        x = graph_x + 20 + q * (graph_width-40) / 150
        y = graph_y + graph_height - 20 - p_val * (graph_height-40) / 50
        demand_points.append((x, y))
    
    # 供给曲线
    for p_val in range(0, 51, 5):
        q_val = base_supply + supply_factor * p_val + supply_shift
        if q_val < 0 or q_val > 150:
            continue
        x = graph_x + 20 + q_val * (graph_width-40) / 150
        y = graph_y + graph_height - 20 - p_val * (graph_height-40) / 50
        supply_points.append((x, y))

    
    # Draw curve lines with thickness
    if len(demand_points) > 1:
        pygame.draw.lines(screen, BLUE, False, demand_points, 3)
    if len(supply_points) > 1:
        pygame.draw.lines(screen, RED, False, supply_points, 3)
    
    # Draw price line
    y_price = graph_y + graph_height - 20 - price * (graph_height-40) / 50
    if graph_x+20 < graph_x+graph_width-20:
        pygame.draw.line(screen, GREEN, (graph_x+20, y_price), (graph_x+graph_width-20, y_price), 2)
    
    # Draw current quantity points
    q_demand = demand(price, demand_shift)
    q_supply = supply(price, supply_shift)
    
    demand_point = (graph_x + 20 + q_demand * (graph_width-40) / 150, y_price)
    supply_point = (graph_x + 20 + q_supply * (graph_width-40) / 150, y_price)
    
    pygame.draw.circle(screen, BLUE, (int(demand_point[0]), int(demand_point[1])), 8)
    pygame.draw.circle(screen, RED, (int(supply_point[0]), int(supply_point[1])), 8)
    
    # Draw curve labels with better positioning
    screen.blit(font.render("需求", True, BLUE), (graph_x+graph_width-100, graph_y+20))
    screen.blit(font.render("供给", True, RED), (graph_x+graph_width-100, graph_y+50))
    screen.blit(font.render(f"价格: ${price:.2f}", True, GREEN), (graph_x+graph_width-150, graph_y+80))


# Draw a button with hover effect
def draw_button(surface, rect, text, hover=False, disabled=False):
    color = BUTTON_HOVER if hover else (BUTTON_DISABLED if disabled else BUTTON_COLOR)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
    
    text_surf = font.render(text, True, WHITE if not disabled else GRAY)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return rect

# Draw a panel with rounded corners
def draw_panel(surface, rect, color, border_color=ACCENT_COLOR, border_width=2):
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=12)

# Add a particle effect
def add_particles(x, y, color, count=10):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 3)
        size = random.randint(2, 5)
        lifetime = random.randint(20, 40)
        particles.append({
            'x': x, 'y': y,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'size': size,
            'color': color,
            'lifetime': lifetime
        })

# Add an achievement
def add_achievement(text):
    achievements.append({
        'text': text,
        'timer': 180,
        'y': 100
    })

# Update particles
def update_particles():
    global particles
    for p in particles[:]:
        p['x'] += p['dx']
        p['y'] += p['dy']
        p['lifetime'] -= 1
        if p['lifetime'] <= 0:
            particles.remove(p)

# Draw particles
def draw_particles(surface):
    for p in particles:
        alpha = min(255, p['lifetime'] * 6)
        color = list(p['color'])
        if len(color) == 3:
            color.append(alpha)
        pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), p['size'])

# Draw achievements
def draw_achievements(surface):
    for ach in achievements[:]:
        panel_width = 300
        panel_height = 50
        x = WIDTH // 2 - panel_width // 2
        y = ach['y']
        
        # Update position
        if ach['y'] > 120:
            ach['y'] -= 1
        
        # Draw panel
        pygame.draw.rect(surface, SECONDARY_COLOR, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=10)
        
        # Draw text
        text = font.render(ach['text'], True, WHITE)
        surface.blit(text, (x + panel_width//2 - text.get_width()//2, y + panel_height//2 - text.get_height()//2))
        
        # Update timer
        ach['timer'] -= 1
        if ach['timer'] <= 0:
            achievements.remove(ach)

# Draw difficulty selector
def draw_difficulty_selector(surface, x, y):
    global difficulty
    
    # Draw panel
    pygame.draw.rect(surface, PANEL_COLOR, (x, y, 300, 50), border_radius=10)
    pygame.draw.rect(surface, ACCENT_COLOR, (x, y, 300, 50), 2, border_radius=10)
    
    # Draw title
    title = font.render("难度:", True, WHITE)
    surface.blit(title, (x + 10, y + 15))
    
    # Draw options
    options = ["简单", "中等", "困难"]
    option_rects = []
    
    for i, option in enumerate(options):
        rect = pygame.Rect(x + 100 + i*60, y+10, 50, 30)
        color = HIGHLIGHT if difficulty == option else PANEL_COLOR
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, ACCENT_COLOR, rect, 1, border_radius=5)
        
        text = font_small.render(option, True, WHITE)
        surface.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
        
        option_rects.append((rect, option))
    
    return option_rects

# 修改后的draw_start_screen函数
def draw_start_screen():
    screen.fill(BACKGROUND)
    
    # Draw title
    title = font_large.render("市场均衡大师", True, ACCENT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))  # 上移标题
    
    # Draw subtitle
    subtitle = font.render("掌握供需平衡，成为市场大师！", True, WHITE)
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 140))  # 上移副标题
    
    # Draw game description - 调整位置和布局
    desc = [
        "游戏规则:",
        "1. 通过滑块设置商品价格",
        "2. 点击提交按钮结束当前回合",
        "3. 根据当前目标（最小化库存或最大化利润）获得积分",
        "4. 随机事件会影响供需曲线",
        "5. 在10轮中尽可能获得高分！"
    ]
    
    # 将规则文本向左移动，避免与按钮重叠
    for i, line in enumerate(desc):
        text = font_ui.render(line, True, WHITE)
        screen.blit(text, (WIDTH//2 - 300, 180 + i*30))  # 调整x坐标
    
    # 调整按钮位置
    start_button = pygame.Rect(WIDTH//2 - 100, 400, 200, 60)  # 下移按钮
    help_button = pygame.Rect(WIDTH//2 - 100, 480, 200, 60)   # 下移按钮
    
    start_hover = start_button.collidepoint(pygame.mouse.get_pos())
    help_hover = help_button.collidepoint(pygame.mouse.get_pos())
    
    draw_button(screen, start_button, "开始游戏", start_hover)
    draw_button(screen, help_button, "游戏帮助", help_hover)
    
    # Draw difficulty selector - 下移
    difficulty_rects = draw_difficulty_selector(screen, WIDTH//2 - 150, 550)
    
    # Draw particles for decoration
    if random.random() < 0.05:
        add_particles(random.randint(100, WIDTH-100), random.randint(200, 500), ACCENT_COLOR, 5)
    
    update_particles()
    draw_particles(screen)
    
    return start_button, help_button, difficulty_rects  # 返回按钮和难度选择器对象

def draw_help_screen():
    global max_help_scroll
    
    screen.fill(BACKGROUND)
    
    # Draw title
    title = font_large.render("游戏帮助", True, ACCENT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    # Draw game instructions
    instructions = [
        "游戏目标:",
        "- 通过调整价格平衡供需关系",
        "- 每轮根据当前目标获得积分",
        "",
        "游戏要素:",
        "- 蓝色曲线: 需求曲线",
        "- 红色曲线: 供给曲线",
        "- 绿色横线: 当前设置的价格",
        "- 蓝色圆点: 当前价格下的需求量",
        "- 红色圆点: 当前价格下的供给量",
        "",
        "积分系统:",
        "- 当目标为'最小化库存'时:",
        "  库存越接近0，得分越高",
        "- 当目标为'最大化利润'时:",
        "  利润越高，得分越高",
        "",
        "随机事件:",
        "- 游戏中的随机事件会影响供需关系",
        "- 事件只持续一个回合",
        "- 注意事件提示并相应调整策略",
        "",
        "操作说明:",
        "- 拖动滑块设置价格",
        "- 点击'提交'按钮结束当前回合",
        "- 时间结束后自动提交",
        "",
        "高级策略:",
        "- 在需求增加事件时提高价格以最大化利润",
        "- 在供应减少事件时降低价格以最小化库存",
        "- 关注库存水平，避免过高或负库存",
        "- 不同难度级别影响事件频率和严重性",
        "",
        "成就系统:",
        "- 在游戏中达成特定条件可获得成就",
        "- 成就包括高分、完美回合等",
        "",
        "提示:",
        "- 在简单难度下，事件影响较小且频率较低",
        "- 在困难难度下，事件更加频繁且影响更大",
        "- 尝试预测事件影响并提前调整策略",
        "",
        "按ESC键或点击下方按钮返回主菜单"
    ]
    
    # Calculate total height
    total_height = len(instructions) * 30
    max_help_scroll = max(0, total_height - 500)  # 500 is available height
    
    # Draw scrollable content
    y_pos = 120 + help_scroll
    for line in instructions:
        text = font_ui.render(line, True, WHITE)
        screen.blit(text, (WIDTH//2 - 300, y_pos))
        y_pos += 30
    
    # Draw scroll bar if needed
    if max_help_scroll > 0:
        # Calculate scroll bar height and position
        bar_height = 500 * 500 / total_height
        bar_pos = 620 - (help_scroll / max_help_scroll) * (500 - bar_height)
        
        # Draw scroll track
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH//2 + 280, 120, 10, 500))
        # Draw scroll bar
        pygame.draw.rect(screen, ACCENT_COLOR, (WIDTH//2 + 280, bar_pos, 10, bar_height), border_radius=5)
    
    # Draw back button
    back_button = pygame.Rect(WIDTH//2 - 100, 650, 200, 40)
    back_hover = back_button.collidepoint(pygame.mouse.get_pos())
    draw_button(screen, back_button, "返回主菜单", back_hover)
    
    return back_button

# Draw game over screen
def draw_game_over_screen():
    screen.fill(BACKGROUND)
    
    # Draw title
    title = font_large.render("游戏结束!", True, ACCENT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    # Draw score
    score_text = font_title.render(f"最终得分: {points:.0f}", True, YELLOW)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 180))
    
    # Draw rating
    rating = ""
    if points < 500:
        rating = "新手"
    elif points < 800:
        rating = "中级"
    elif points < 1000:
        rating = "专家"
    else:
        rating = "市场大师!"
        if "市场大师" not in [a['text'] for a in achievements]:
            add_achievement("成就: 市场大师!")
    
    rating_text = font_title.render(f"评级: {rating}", True, GREEN)
    screen.blit(rating_text, (WIDTH//2 - rating_text.get_width()//2, 230))
    
    # Draw stats
    pygame.draw.rect(screen, PANEL_COLOR, (WIDTH//2 - 200, 280, 400, 200), border_radius=15)
    pygame.draw.rect(screen, ACCENT_COLOR, (WIDTH//2 - 200, 280, 400, 200), 2, border_radius=15)
    
    stats = [
        f"总利润: ${profit:.2f}",
        f"最终库存: {inventory:.1f}",
        f"难度: {difficulty}"
    ]
    
    for i, stat in enumerate(stats):
        text = font.render(stat, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 310 + i*50))
    
    # Draw history panel
    if history:
        pygame.draw.rect(screen, PANEL_COLOR, (WIDTH//2 - 200, 500, 400, 150), border_radius=15)
        pygame.draw.rect(screen, ACCENT_COLOR, (WIDTH//2 - 200, 500, 400, 150), 2, border_radius=15)
        
        # Draw column headers
        headers = ["回合", "价格", "需求", "供给", "积分"]
        header_width = 80
        for i, header in enumerate(headers):
            x_pos = WIDTH//2 - 180 + i * header_width
            text = font_small.render(header, True, ACCENT_COLOR)
            screen.blit(text, (x_pos, 520))
        
        # Draw last 3 rounds
        start_idx = max(0, len(history) - 3)
        for j, entry in enumerate(history[start_idx:]):
            y_pos = 550 + j * 30
            data = [
                str(entry['round']),
                f"${entry['price']:.1f}",
                f"{entry['demand']:.1f}",
                f"{entry['supply']:.1f}",
                f"{entry['points']:.0f}"
            ]
            
            for i, value in enumerate(data):
                x_pos = WIDTH//2 - 180 + i * header_width
                text = font_small.render(value, True, WHITE)
                screen.blit(text, (x_pos, y_pos))
    
    # Draw restart button
    restart_hover = restart_button.collidepoint(pygame.mouse.get_pos())
    draw_button(screen, restart_button, "重新开始", restart_hover)
    
    # Draw particles for celebration
    if random.random() < 0.1 and points > 700:
        add_particles(random.randint(200, WIDTH-200), 150, YELLOW, 3)
    
    update_particles()
    draw_particles(screen)

# Draw round transition screen
def draw_round_transition():
    screen.fill(BACKGROUND)
    
    # Draw title
    title = font_large.render(f"第 {rounds} 回合结果", True, ACCENT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    # Draw result panel
    pygame.draw.rect(screen, PANEL_COLOR, (WIDTH//2 - 200, 180, 400, 300), border_radius=15)
    pygame.draw.rect(screen, ACCENT_COLOR, (WIDTH//2 - 200, 180, 400, 300), 3, border_radius=15)
    
    # Draw result info
    if current_round_result:
        result = current_round_result
        items = [
            f"设置价格: ${result['price']:.2f}",
            f"需求量: {result['demand']:.1f}",
            f"供给量: {result['supply']:.1f}",
            f"库存变化: {result['inventory_change']:+.1f}",
            f"利润变化: ${result['profit_change']:.2f}",
            f"获得积分: {result['points']:.0f}",
            "",
            f"下回合目标: {next_round_goal}",
            f"下回合事件: {next_round_event[0]}"
        ]
        
        for i, item in enumerate(items):
            text = font.render(item, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 220 + i * 35))
    
    # Draw continue button
    continue_button = pygame.Rect(WIDTH//2 - 100, 520, 200, 50)
    continue_hover = continue_button.collidepoint(pygame.mouse.get_pos())
    draw_button(screen, continue_button, "继续游戏", continue_hover)
    
    return continue_button

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks() / 1000
    dt = min(0.05, current_time - last_time)
    last_time = current_time
    
    if game_state == "playing" and not round_completed:
        timer -= dt
        if timer <= 0 and not round_completed:
            # 时间结束自动提交
            submit_round = True
    
    # Handle events
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if help_open:
                    help_open = False
                elif game_state == "playing":
                    game_state = "start"
                elif game_state == "game_over":
                    game_state = "start"
                elif game_state == "round_transition":
                    game_state = "playing"
            elif event.key == pygame.K_RETURN and game_state == "playing" and not round_completed:
                # 按回车键提交
                submit_round = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                # 获取按钮和难度选择器
                start_button, help_button, difficulty_rects = draw_start_screen()
                
                if start_button.collidepoint(event.pos):
                    game_state = "playing"
                    price, inventory, profit, rounds, points = 20, 100, 0, 0, 0
                    slider_x, timer = 300, 60
                    event_message, demand_shift, supply_shift = "没有事件", 0, 0
                    history = []
                    round_completed = False
                    # Set first event
                    event_message, demand_shift, supply_shift = apply_random_event()
                    goal = random.choice(["最小化库存", "最大化利润"])
                elif help_button.collidepoint(event.pos):
                    help_open = True
                    help_scroll = 0  # 重置滚动位置
                    
                # 检查难度选择
                for rect, option in difficulty_rects:
                    if rect.collidepoint(event.pos):
                        difficulty = option
                        
            elif game_state == "playing":
                # 优先处理按钮点击
                if restart_button.collidepoint(event.pos):
                    price, inventory, profit, rounds, points = 20, 100, 0, 0, 0
                    slider_x, timer = 300, 60
                    event_message, demand_shift, supply_shift = "没有事件", 0, 0
                    history = []
                    round_completed = False
                    # Set first event
                    event_message, demand_shift, supply_shift = apply_random_event()
                    goal = random.choice(["最小化库存", "最大化利润"])
                elif submit_button.collidepoint(event.pos) and not round_completed:
                    # 提交按钮点击
                    submit_round = True
                elif 50 <= event.pos[0] <= 600 and 470 <= event.pos[1] <= 500:  # 滑块位置调整
                    dragging = True
                    
            elif game_state == "game_over":
                if restart_button.collidepoint(event.pos):
                    game_state = "playing"
                    price, inventory, profit, rounds, points = 20, 100, 0, 0, 0
                    slider_x, timer = 300, 60
                    event_message, demand_shift, supply_shift = "没有事件", 0, 0
                    history = []
                    round_completed = False
                    # Set first event
                    event_message, demand_shift, supply_shift = apply_random_event()
                    goal = random.choice(["最小化库存", "最大化利润"])
            
            if help_open:
                back_button = draw_help_screen()
                if back_button.collidepoint(event.pos):
                    help_open = False
                # 处理滚轮事件
                elif event.button == 4:  # 向上滚动
                    help_scroll = min(0, help_scroll + 20)
                elif event.button == 5:  # 向下滚动
                    help_scroll = max(-max_help_scroll, help_scroll - 20)
                    
            elif game_state == "round_transition":
                continue_button = draw_round_transition()
                if continue_button.collidepoint(event.pos):
                    game_state = "playing"
                    round_completed = False
                    # Apply next round event
                    event_message, demand_shift, supply_shift = next_round_event
                    goal = next_round_goal
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            
        elif event.type == pygame.MOUSEMOTION and dragging and game_state == "playing":
            slider_x = max(50, min(600, event.pos[0]))
            price = (slider_x - 50) / 550 * 50
    
    # 处理提交回合
    if 'submit_round' in locals() and not round_completed:
        q_demand = demand(price, demand_shift)
        q_supply = supply(price, supply_shift)
        profit_change = q_demand * price - q_supply * 10
        inventory_change = q_supply - q_demand
        inventory += inventory_change
        profit += profit_change
        
        # Calculate points
        if goal == "最小化库存":
            round_points = max(0, 100 - abs(inventory_change) * 2)
        else:  # Maximize Profit
            round_points = max(0, profit_change * 0.1)
        
        points += round_points
        
        # Store round result
        current_round_result = {
            'round': rounds + 1,
            'price': price,
            'demand': q_demand,
            'supply': q_supply,
            'inventory_change': inventory_change,
            'profit_change': profit_change,
            'points': round_points
        }
        
        # Add to history
        history.append(current_round_result)
        
        rounds += 1
        round_completed = True
        
        # Prepare next round
        next_round_event = apply_random_event()
        next_round_goal = random.choice(["最小化库存", "最大化利润"])
        
        # Add particles for feedback
        add_particles(slider_x, 470, GREEN if round_points > 50 else YELLOW, 15)
        
        # Add achievements
        if round_points > 90 and "完美决策" not in [a['text'] for a in achievements]:
            add_achievement("成就: 完美决策!")
        if profit_change > 500 and "高额利润" not in [a['text'] for a in achievements]:
            add_achievement("成就: 高额利润!")
        
        # Enter transition screen
        game_state = "round_transition"
        round_transition_time = pygame.time.get_ticks()
        
        # Reset timer for next round
        timer = 60
        
        # Clear submit flag
        del submit_round
    
    # Drawing
    screen.fill(BACKGROUND)
    
    if game_state == "start" and not help_open:
        draw_start_screen()
    elif help_open:
        back_button = draw_help_screen()
    elif game_state == "round_transition":
        continue_button = draw_round_transition()
    elif game_state == "playing":
        # Draw background elements
        for i in range(20):
            x = (pygame.time.get_ticks() / 50 + i * 100) % (WIDTH + 200) - 100
            y = 100 + i * 30
            pygame.draw.circle(screen, (30, 50, 80, 30), (int(x), int(y)), 2)
        
        # Draw curves
        draw_curves(screen, price)
        
        # 计算当前需求量和供给量
        q_demand = demand(price, demand_shift)
        q_supply = supply(price, supply_shift)
    
        # 计算状态
        if abs(q_demand - q_supply) < 5:
            status = "均衡"
        elif q_supply > q_demand:
            status = "过剩"
        else:
            status = "短缺"

        # Draw right panel
        # 重新设计右侧面板布局
        right_panel_x = 620
        right_panel_width = 350
        right_panel_height = 400
    
        pygame.draw.rect(screen, PANEL_COLOR, (right_panel_x, 50, right_panel_width, right_panel_height), border_radius=12)
        pygame.draw.rect(screen, ACCENT_COLOR, (right_panel_x, 50, right_panel_width, right_panel_height), 2, border_radius=12)

        # 使用表格形式展示信息
        headers = ["指标", "值"]
        col1_x = right_panel_x + 20
        col2_x = right_panel_x + 150
        # 绘制表头
        pygame.draw.line(screen, ACCENT_COLOR, (col1_x, 80), (col1_x+300, 80), 2)
        screen.blit(font.render(headers[0], True, ACCENT_COLOR), (col1_x, 60))
        screen.blit(font.render(headers[1], True, ACCENT_COLOR), (col2_x, 60))

        # 绘制信息行
        info_rows = [
            ("需求", f"{q_demand:.1f}"),
            ("供给", f"{q_supply:.1f}"),
            ("状态", status),
            ("库存", f"{inventory:.1f}"),
            ("利润", f"${profit:.2f}"),
            ("积分", f"{points:.0f}"),
                ("回合", f"{rounds}/{max_rounds}"),
            ("时间", f"{timer:.1f}s"),
            ("目标", goal),
            ("事件", event_message)
        ]    
        
        for i, (label, value) in enumerate(info_rows):
            y_pos = 100 + i * 30
            screen.blit(font.render(label, True, WHITE), (col1_x, y_pos))
        
            # 特殊行的颜色
            if label == "状态":
                color = GREEN if status == "均衡" else YELLOW
            elif label == "目标":
                color = YELLOW if goal == "最大化利润" else GREEN
            else:
                color = WHITE
            
            screen.blit(font.render(value, True, color), (col2_x, y_pos))
    
        # 调整按钮位置
        button_y = 520
        button_width = 150
        button_height = 45
    
        # 提交按钮
        submit_button = pygame.Rect(right_panel_x + 20, button_y, button_width, button_height)
        submit_hover = submit_button.collidepoint(mouse_pos)
        draw_button(screen, submit_button, "提交回合", submit_hover, round_completed)
    
        # 重新开始按钮
        restart_button = pygame.Rect(right_panel_x + 190, button_y, button_width, button_height)
        restart_hover = restart_button.collidepoint(mouse_pos)
        draw_button(screen, restart_button, "重新开始", restart_hover)
    
        # 绘制滑块（在图表下方）
        slider_y = 470
        slider_width = 550
        slider_height = 20
    
        # 绘制滑块轨道
        pygame.draw.rect(screen, LIGHT_GRAY, (50, slider_y, slider_width, slider_height), border_radius=5)
        
        # 绘制滑块手柄
        pygame.draw.rect(screen, YELLOW, (slider_x - 15, slider_y - 5, 30, slider_height + 10), border_radius=5)
        pygame.draw.circle(screen, HIGHLIGHT, (int(slider_x), slider_y + slider_height//2), 8)
        screen.blit(font.render(f"${price:.2f}", True, WHITE), (slider_x - 25, slider_y - 30))
    
        # 历史记录面板调整
        history_panel_y = slider_y + slider_height + 20
        pygame.draw.rect(screen, PANEL_COLOR, (50, history_panel_y, slider_width, 40), border_radius=10)
        pygame.draw.rect(screen, ACCENT_COLOR, (50, history_panel_y, slider_width, 40), 2, border_radius=10)
    
        if history:
            start_idx = max(0, len(history) - 6)  # 显示最多6个回合
            for i, entry in enumerate(history[start_idx:]):
                x_pos = 70 + i * 90
                # 使用更紧凑的格式
                text = font_small.render(f"R{entry['round']}:${entry['price']:.1f}", True, WHITE)
                screen.blit(text, (x_pos, history_panel_y + 20))
        
        # Update and draw particles
        update_particles()
        draw_particles(screen)
        
        # Draw achievements
        draw_achievements(screen)
        
        # Check game over
        if rounds >= max_rounds:
            game_state = "game_over"
    
    elif game_state == "game_over":
        draw_game_over_screen()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
