市场均衡大师游戏说明文档
游戏背景与经济学原理
市场均衡大师 是一款教育类游戏，旨在通过模拟市场供需动态教授微观经济学基础知识。玩家通过调整商品价格，平衡供需关系，应对随机经济事件，实现目标（如最小化库存或最大化利润）。
应用的经济学原理

供需曲线：游戏使用向下倾斜的需求曲线（demand = base_demand - demand_factor * price + demand_shift）和向上倾斜的供给曲线（supply = base_supply + supply_factor * price + supply_shift），反映价格与需求量、供给量的关系。
市场均衡：玩家需设定价格使供需平衡，减少过剩（供给过量）或短缺（需求过量）。
随机事件：如干旱或节日等事件会移动供需曲线，模拟现实中的经济波动。
目标：交替的目标（如最小化库存或最大化利润）教会玩家权衡定价决策。

核心玩法与机制
游戏概述

目标：在10轮游戏中，玩家通过滑块设定价格，根据目标（最小化库存或最大化利润）获得积分。
游戏状态：包括开始界面、游戏进行、回合过渡、游戏结束和帮助界面。
随机事件：每轮会有事件（如“干旱减少供应”）影响供需曲线，需调整价格策略。
难度等级：简单、中等、困难模式调整事件频率和影响，兼顾可玩性和挑战性。
计分：根据目标达成情况得分，例如“最小化库存”目标下，库存变化越小得分越高。
成就系统：达成特定条件（如高分回合）可解锁成就，增加趣味性。

核心机制

价格设定：玩家拖动滑块设定价格（0到50），在供需曲线上可视化显示。
实时反馈：图表显示当前价格、需求量和供给量，并标示状态（均衡、过剩、短缺）。
时间限制：每轮60秒，倒计时结束自动提交。
库存与利润跟踪：库存根据供给减需求变化，利润考虑收入减成本。
历史记录：历史面板记录过去回合的价格、数量和积分，供玩家分析。
视觉效果：粒子动画和成就弹窗提升用户体验。

如何运行与操作游戏
运行要求

Python：版本3.6或更高。
库：
pygame：用于图形渲染和输入处理。
numpy：用于供需函数的数值计算。
random 和 math：标准库，用于随机事件和粒子计算。
sys：用于系统退出处理。



安装步骤

从 python.org 安装 Python。
安装所需库：pip install pygame numpy


将游戏代码保存为 market_equilibrium.py。

运行游戏

运行脚本：python market_equilibrium.py


游戏窗口（1000x700像素）将打开，标题为“市场均衡大师”。

操作说明

开始界面：
点击“开始游戏”进入游戏。
点击“游戏帮助”查看说明。
点击“简单”、“中等”或“困难”选择难度。


游戏进行：
拖动滑块设定价格。
点击“提交回合”或按 Enter 提交回合。
点击“重新开始”重启游戏。
按 ESC 返回开始界面。


帮助界面：
使用鼠标滚轮滚动查看说明。
点击“返回主菜单”或按 ESC 返回。


游戏结束：
点击“重新开始”重新游戏。



代码结构与关键组件
使用的外部库

pygame：处理图形（绘制曲线、按钮、面板）、用户输入（鼠标、键盘）和游戏循环。
numpy：在 demand 和 supply 函数中进行高效数值计算。
random：生成随机事件和粒子效果。
math：支持粒子运动计算。
sys：确保游戏正常退出。

模块划分
代码为单一 Python 脚本，通过函数模块化组织：

初始化：

初始化 Pygame、屏幕（1000x700）、字体（SimHei 支持中文）和颜色。
定义游戏变量（价格、库存、利润、回合数等）。


经济函数：

demand(price, shift)：根据价格和需求偏移计算需求量。
supply(price, shift)：根据价格和供给偏移计算供给量。
apply_random_event()：根据难度加权选择随机事件，返回事件描述和曲线偏移。


绘制函数：

draw_curves(screen, price)：在550x400像素图表上绘制供需曲线、轴和价格线。
draw_button(surface, rect, text, hover, disabled)：绘制带悬停/禁用状态的交互按钮。
draw_panel(surface, rect, color, border_color)：绘制圆角面板用于 UI 元素。
draw_particles(surface) 和 update_particles()：管理粒子效果，提供视觉反馈。
draw_achievements(surface)：显示临时成就通知。
draw_difficulty_selector(surface, x, y)：渲染难度选择界面。
draw_start_screen()、draw_help_screen()、draw_game_over_screen()、draw_round_transition()：处理不同游戏状态的 UI。


主游戏循环：

管理游戏状态（“start”、“playing”、“round_transition”、“game_over”、“help”）。
处理事件（鼠标点击、键盘输入、滑块拖动）。
更新计时器，处理回合提交和回合过渡。
根据游戏状态渲染相应界面。



关键代码段

曲线绘制（draw_curves）：
demand_points = [(graph_x + 20 + q * (graph_width-40) / 150, graph_y + graph_height - 20 - p_val * (graph_height-40) / 50) for q in range(0, 151, 5) if 0 <= p_val <= 50]
pygame.draw.lines(screen, BLUE, False, demand_points, 3)

将经济函数映射到屏幕坐标，绘制平滑曲线。

事件处理：
if event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
    if submit_button.collidepoint(event.pos) and not round_completed:
        submit_round = True

检测按钮点击以提交回合或调整价格滑块。

回合提交：
q_demand = demand(price, demand_shift)
q_supply = supply(price, supply_shift)
inventory_change = q_supply - q_demand
profit_change = q_demand * price - q_supply * 10
points += max(0, 100 - abs(inventory_change) * 2) if goal == "minimize inventory" else max(0, profit_change * 0.1)

计算回合结果并更新游戏状态。


设计理念

教育导向：通过可视化曲线和实时反馈简化复杂的经济学概念。
用户参与：结合清晰的 UI、粒子效果和成就系统，使学习过程有趣。
模块化：函数组织清晰，便于阅读和维护。
可扩展性：难度等级和随机事件提供多样化的游戏体验。

结论
市场均衡大师 通过引人入胜的视觉效果和交互性有效教授供需原理。其模块化代码结构和清晰的文档便于运行、修改或扩展。游戏平衡了教育价值和娱乐性，适合学生和经济学爱好者。
