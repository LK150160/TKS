import pygame
import random
import sys
from enum import Enum
import ctypes  # 用于获取屏幕分辨率
import os
import pkg_resources  # 用于处理打包后的资源文件

# 初始化pygame，包括音频模块
pygame.init()
pygame.mixer.init()  # 初始化音频混合器

# 确保中文显示正常
pygame.font.init()
font_options = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS"]
BASE_FONT_SIZE = 15  # 统一设置字体大小为15
font = None
for font_name in font_options:
    try:
        font = pygame.font.SysFont(font_name, BASE_FONT_SIZE)
        if font:
            break
    except:
        continue
if not font:
    font = pygame.font.Font(None, BASE_FONT_SIZE)  # 使用默认字体作为备选

# 播放背景音乐函数 - 优化资源路径处理，确保打包后可用
def play_background_music():
    """尝试播放背景音乐，返回是否播放成功"""
    try:
        # 尝试多种路径获取方式，确保打包后仍能找到音乐文件
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            base_path = sys._MEIPASS
            music_path = os.path.join(base_path, "1.flac")
        else:
            # 开发环境
            # 尝试当前目录
            if os.path.exists("1.flac"):
                music_path = "1.flac"
            else:
                # 尝试通过pkg_resources获取
                music_path = pkg_resources.resource_filename(__name__, "1.flac")
        
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)  # 设置音量为50%
        pygame.mixer.music.play(-1)  # -1表示循环播放
        return True
    except Exception as e:
        print(f"无法播放音乐: {e}")
        return False

# 获取屏幕分辨率
def get_screen_resolution():
    """获取当前屏幕的分辨率"""
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_resolution()

# 常量定义
MAP_SIZE = 50
BASE_CELL_SIZE = 15  # 基础单元格大小
BASE_INFO_WIDTH = 300  # 基础信息面板宽度

# 计算初始缩放比例 - 确保窗口能完整显示在屏幕上
def calculate_initial_scale():
    """计算初始缩放比例，确保窗口不会超出屏幕"""
    base_window_width = MAP_SIZE * BASE_CELL_SIZE + BASE_INFO_WIDTH
    base_window_height = MAP_SIZE * BASE_CELL_SIZE
    
    # 基于屏幕宽度和高度计算可能的最大缩放比例
    scale_by_width = SCREEN_WIDTH / base_window_width
    scale_by_height = SCREEN_HEIGHT / base_window_height
    
    # 取较小的缩放比例，确保窗口能完整显示，最大不超过1.0
    return min(min(scale_by_width, scale_by_height), 1.0)

INITIAL_SCALE = calculate_initial_scale()

# 计算实际窗口尺寸
WINDOW_WIDTH = int((MAP_SIZE * BASE_CELL_SIZE + BASE_INFO_WIDTH) * INITIAL_SCALE)
WINDOW_HEIGHT = int(MAP_SIZE * BASE_CELL_SIZE * INITIAL_SCALE)

# 游戏参数设置 - 调整单位平衡
INITIAL_TERRITORY_SIZE = 8  # 初始领土大小（正方形边长）
# 各派系人口上限和单位属性平衡调整
# 交换了蜀国和魏国的单位上限
MAX_UNITS_SHU = 50    # 蜀国（原魏国矮人）上限
MAX_UNITS_WEI = 30    # 魏国（原蜀国巨人）上限
MAX_UNITS_WU = 45     # 吴国棒球人上限

# 颜色定义（优化色彩，增强视觉效果）
COLORS = {
    'SHU': (0, 180, 0),        # 蜀 - 深绿色（更鲜明）
    'SHU_LAND': (144, 238, 144),  # 蜀占领地 - 淡绿色
    'WEI': (128, 0, 128),      # 魏 - 紫色
    'WEI_LAND': (216, 191, 216),  # 魏占领地 - 淡紫色
    'WU': (200, 0, 0),         # 吴 - 深红色（更鲜明）
    'WU_ELITE': (139, 0, 0),   # 吴 - 深红色（棒球棍大哥）
    'WU_LAND': (255, 160, 122),   # 吴占领地 - 淡红色
    'EMPTY': (230, 230, 230),  # 空地 - 浅灰色（更柔和）
    'TEXT': (50, 50, 50),      # 文字 - 深灰色（更易读）
    'BACKGROUND': (250, 250, 250),  # 背景 - 极浅灰色（减轻视觉疲劳）
    'HIGHLIGHT': (255, 215, 0),   # 高亮 - 金色（更美观）
    'MUSIC_BUTTON': (220, 220, 255),  # 音乐按钮背景色
    'MUSIC_BUTTON_HIGHLIGHT': (180, 180, 255),  # 音乐按钮高亮色
    'PANEL_BORDER': (200, 200, 200),  # 面板边框
    'PANEL_HEADER': (240, 240, 240),  # 面板标题背景
    'RANK_1': (255, 215, 0),   # 第一名 - 金色
    'RANK_2': (192, 192, 192), # 第二名 - 银色
    'RANK_3': (184, 115, 51),  # 第三名 - 铜色
    'SEPARATOR': (220, 220, 220) # 分隔线
}

# 游戏模式
class GameMode(Enum):
    TWO_WEAK_AGAINST_STRONG = "模式一：两弱联合抗强"
    AI_AUTONOMOUS_ALLIANCE = "模式二：AI自主选择联合对象"

# 派系枚举
class Faction(Enum):
    SHU = "蜀"
    WEI = "魏"
    WU = "吴"
    EMPTY = "空地"

# 外交状态
class DiplomaticStatus(Enum):
    PEACE = "和平"
    WAR = "交战"
    ALLIANCE = "联盟"

# 外交请求
class DiplomaticRequest:
    def __init__(self, sender, receiver, request_type):
        self.sender = sender  # 请求发送方派系管理器
        self.receiver = receiver  # 请求接收方派系管理器
        self.request_type = request_type  # 请求类型："停战"、"结盟"等
        self.status = "pending"  # 状态：pending, accepted, rejected
        self.turns_pending = 0  # 等待的回合数

# 单位类
class Unit:
    def __init__(self, faction, x, y):
        self.faction = faction
        self.x = x
        self.y = y
        
        # 调整单位属性，增强平衡性
        # 交换了蜀国和魏国的兵种数值
        if faction == Faction.SHU:  # 蜀 - 现在使用原魏国矮人的属性
            self.attack = 2  # 原魏国矮人的攻击力
            self.health = 5  # 原魏国矮人的生命值
            self.population_cost = 2  # 原魏国矮人的人口成本
            self.movement_range = 2  # 原魏国矮人的移动范围
            self.unit_type = "矮人"  # 原魏国矮人的单位类型
        elif faction == Faction.WEI:  # 魏 - 现在使用原蜀国巨人的属性
            self.attack = 7  # 原蜀国巨人的攻击力
            self.health = 35  # 原蜀国巨人的生命值
            self.population_cost = 6  # 原蜀国巨人的人口成本
            self.movement_range = 1  # 原蜀国巨人的移动范围
            self.unit_type = "巨人"  # 原蜀国巨人的单位类型
        elif faction == Faction.WU:  # 吴 - 棒球人（保持不变）
            # 25%概率生成棒球棍大哥
            if random.random() < 0.25:
                self.attack = 10
                self.health = 12
                self.unit_type = "棒球棍大哥"
            else:
                self.attack = 8
                self.health = 7
                self.unit_type = "普通人"
            self.population_cost = 4
            self.movement_range = 2

    def move(self, dx, dy, map_grid, land_grid):
        """移动单位，检查是否可以移动到新位置"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 检查是否在地图范围内
        if 0 <= new_x < MAP_SIZE and 0 <= new_y < MAP_SIZE:
            # 检查目标位置是否为空
            if map_grid[new_y][new_x] is None:
                # 移动单位
                old_x, old_y = self.x, self.y
                self.x = new_x
                self.y = new_y
                
                # 更新土地所有权 - 单位移动后，原位置和新位置都归该派系所有
                land_grid[old_y][old_x] = self.faction
                land_grid[new_y][new_x] = self.faction
                
                return True
        return False
    
    def attack_unit(self, target):
        """攻击另一个单位"""
        target.health -= self.attack
        return target.health <= 0  # 返回目标是否被消灭

# 派系管理类
class FactionManager:
    def __init__(self, faction, start_x, start_y, size):
        self.faction = faction  # 派系枚举值
        self.units = []
        self.land = 0  # 拥有的地皮数量
        self.population = 0  # 人口数量
        self.start_x = start_x  # 初始领土起始x坐标
        self.start_y = start_y  # 初始领土起始y坐标
        self.size = size        # 初始领土大小
        
        # 外交关系 - 与其他派系的关系
        self.diplomacy = {
            Faction.SHU: DiplomaticStatus.PEACE,
            Faction.WEI: DiplomaticStatus.PEACE,
            Faction.WU: DiplomaticStatus.PEACE
        }
        
        # 联盟持续时间（用于增强联盟稳定性）
        self.alliance_turns = {
            Faction.SHU: 0,
            Faction.WEI: 0,
            Faction.WU: 0
        }
        
        # 记录上一回合的土地数量，用于计算变化
        self.previous_land = 0
        
        # 根据派系设置单位上限（已交换蜀国和魏国的上限）
        if faction == Faction.SHU:
            self.max_units = MAX_UNITS_SHU  # 现在是原魏国的上限
        elif faction == Faction.WEI:
            self.max_units = MAX_UNITS_WEI  # 现在是原蜀国的上限
        else:  # WU
            self.max_units = MAX_UNITS_WU
        
        # 初始5个单位
        self.initialize_units()
    
    def initialize_units(self):
        """在指定的初始领土范围内初始化5个单位"""
        for _ in range(5):
            # 在初始领土范围内随机位置生成单位
            while True:
                x = random.randint(self.start_x, self.start_x + self.size - 1)
                y = random.randint(self.start_y, self.start_y + self.size - 1)
                
                # 确保不超出地图范围
                x = max(0, min(x, MAP_SIZE - 1))
                y = max(0, min(y, MAP_SIZE - 1))
                
                # 检查是否已被占用
                position_taken = False
                for unit in self.units:
                    if unit.x == x and unit.y == y:
                        position_taken = True
                        break
                        
                if not position_taken:
                    new_unit = Unit(self.faction, x, y)
                    self.units.append(new_unit)
                    self.population += new_unit.population_cost
                    break
    
    def calculate_strength(self):
        """计算实力 = 地皮数量 + 人口数量 + 单位战斗力加权值（已调整蜀国和魏国的权重）"""
        unit_strength = 0
        for unit in self.units:
            # 不同单位类型有不同的战斗力权重（已交换蜀国和魏国的单位权重）
            if unit.unit_type == "巨人":  # 现在是魏国的单位
                unit_strength += 5  # 巨人权重高
            elif unit.unit_type == "棒球棍大哥":  # 吴国精英单位
                unit_strength += 4  # 精英单位次高
            elif unit.unit_type == "普通人":  # 吴国普通单位
                unit_strength += 2  # 普通单位中等
            elif unit.unit_type == "矮人":  # 现在是蜀国的单位
                unit_strength += 1  # 矮人权重低，但数量多
        
        # 综合计算实力
        return int(self.land * 0.7 + self.population * 0.5 + unit_strength)
    
    def add_unit(self, x, y, land_grid):
        """添加新单位并标记土地所有权"""
        # 检查是否已达到兵力上限
        if len(self.units) >= self.max_units:
            return None
            
        new_unit = Unit(self.faction, x, y)
        self.units.append(new_unit)
        self.population += new_unit.population_cost
        # 新单位位置标记为该派系所有
        land_grid[y][x] = self.faction
        return new_unit
    
    def remove_unit(self, unit):
        """移除单位"""
        if unit in self.units:
            self.population -= unit.population_cost
            self.units.remove(unit)
    
    def update_land_count(self, land_grid):
        """更新拥有的地皮数量，同时记录上一回合的数量用于计算变化"""
        self.previous_land = self.land  # 保存当前值作为上一回合的土地数量
        self.land = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if land_grid[y][x] == self.faction:
                    self.land += 1
    
    def get_land_change(self):
        """返回与上一回合相比的土地变化量"""
        return self.land - self.previous_land
    
    def set_diplomacy_status(self, other_faction, status):
        """设置与其他派系的外交状态"""
        if other_faction != self.faction and other_faction != Faction.EMPTY:  # 不能与自己或空地设置外交状态
            # 如果建立联盟，记录开始时间
            if status == DiplomaticStatus.ALLIANCE:
                self.alliance_turns[other_faction] = 0
            # 如果解除联盟，重置计数器
            elif self.diplomacy[other_faction] == DiplomaticStatus.ALLIANCE and status != DiplomaticStatus.ALLIANCE:
                self.alliance_turns[other_faction] = 0
                
            self.diplomacy[other_faction] = status
    
    def get_diplomacy_status(self, other_faction):
        """获取与其他派系的外交状态"""
        if other_faction == Faction.EMPTY:  # 空地没有外交关系
            return None
        return self.diplomacy[other_faction]
    
    def is_at_war(self, other_faction):
        """检查是否与其他派系处于交战状态"""
        if other_faction == Faction.EMPTY:  # 空地没有外交关系
            return False
        return self.diplomacy[other_faction] == DiplomaticStatus.WAR
    
    def is_allied(self, other_faction):
        """检查是否与其他派系处于联盟状态"""
        if other_faction == Faction.EMPTY:  # 空地没有外交关系
            return False
        return self.diplomacy[other_faction] == DiplomaticStatus.ALLIANCE
    
    def update_alliance_turns(self):
        """更新联盟持续时间"""
        for faction in self.alliance_turns:
            if faction != self.faction and self.is_allied(faction):
                self.alliance_turns[faction] += 1

# 模式选择界面
class ModeSelection:
    def __init__(self, screen, scale):
        self.screen = screen
        self.scale = scale
        self.running = True
        self.selected_mode = None
        
        # 按钮样式优化
        button_width = 300 * scale
        button_height = 60 * scale
        button_y1 = 200 * scale
        button_y2 = 300 * scale
        
        self.buttons = [
            {
                "rect": pygame.Rect(
                    (screen.get_width() - button_width) / 2, 
                    button_y1, 
                    button_width, 
                    button_height
                ),
                "text": GameMode.TWO_WEAK_AGAINST_STRONG.value,
                "mode": GameMode.TWO_WEAK_AGAINST_STRONG
            },
            {
                "rect": pygame.Rect(
                    (screen.get_width() - button_width) / 2, 
                    button_y2, 
                    button_width, 
                    button_height
                ),
                "text": GameMode.AI_AUTONOMOUS_ALLIANCE.value,
                "mode": GameMode.AI_AUTONOMOUS_ALLIANCE
            }
        ]
        
        # 设置字体（保持15px基准，按缩放比例调整）
        self.font = self._get_scaled_font()
        
        # 音乐按钮相关
        self.music_button_radius = int(20 * scale)
        self.update_music_button_position()
        self.music_playing = pygame.mixer.music.get_busy()

    def update_music_button_position(self):
        """更新音乐按钮位置（右上角）"""
        self.music_button_pos = (
            self.screen.get_width() - self.music_button_radius - 10 * self.scale,
            self.music_button_radius + 10 * self.scale
        )

    def _get_scaled_font(self):
        """获取按当前缩放比例调整的字体（保持15px基准）"""
        font_size = max(10, int(BASE_FONT_SIZE * self.scale))
        for font_name in font_options:
            try:
                return pygame.font.SysFont(font_name, font_size)
            except:
                continue
        return pygame.font.Font(None, font_size)
    
    def draw_music_button(self):
        """绘制音乐控制按钮"""
        # 按钮背景
        color = COLORS['MUSIC_BUTTON_HIGHLIGHT'] if self.is_music_button_hovered() else COLORS['MUSIC_BUTTON']
        pygame.draw.circle(
            self.screen, 
            color, 
            (int(self.music_button_pos[0]), int(self.music_button_pos[1])), 
            self.music_button_radius
        )
        pygame.draw.circle(
            self.screen, 
            COLORS['TEXT'], 
            (int(self.music_button_pos[0]), int(self.music_button_pos[1])), 
            self.music_button_radius, 
            2  # 边框宽度
        )
        
        # 绘制音乐图标
        music_icon = "🎵"
        text_surface = self.font.render(music_icon, True, COLORS['TEXT'])
        text_rect = text_surface.get_rect(center=self.music_button_pos)
        self.screen.blit(text_surface, text_rect)
        
        # 如果音乐暂停，显示暂停指示
        if not self.music_playing:
            # 绘制一个简单的暂停符号
            bar_width = int(self.music_button_radius * 0.3)
            bar_height = int(self.music_button_radius * 0.6)
            bar1_x = self.music_button_pos[0] - bar_width - int(self.scale * 2)
            bar2_x = self.music_button_pos[0] + int(self.scale * 2)
            
            pygame.draw.rect(
                self.screen, 
                (200, 0, 0),  # 红色指示暂停
                (bar1_x, self.music_button_pos[1] - bar_height // 2, 
                 bar_width, bar_height)
            )
            pygame.draw.rect(
                self.screen, 
                (200, 0, 0),  # 红色指示暂停
                (bar2_x, self.music_button_pos[1] - bar_height // 2, 
                 bar_width, bar_height)
            )
    
    def is_music_button_hovered(self):
        """检查鼠标是否悬停在音乐按钮上"""
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.music_button_pos[0]
        dy = mouse_pos[1] - self.music_button_pos[1]
        distance = (dx**2 + dy**2)** 0.5
        return distance <= self.music_button_radius
    
    def toggle_music(self):
        """切换音乐播放状态"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
    
    def draw(self):
        """绘制模式选择界面（优化视觉效果）"""
        self.screen.fill(COLORS['BACKGROUND'])
        
        # 绘制标题面板
        title_panel_height = 120 * self.scale
        title_panel = pygame.Rect(0, 0, self.screen.get_width(), title_panel_height)
        pygame.draw.rect(self.screen, COLORS['PANEL_HEADER'], title_panel)
        pygame.draw.line(
            self.screen, 
            COLORS['SEPARATOR'], 
            (0, title_panel_height), 
            (self.screen.get_width(), title_panel_height), 
            int(2 * self.scale)
        )
        
        # 标题
        title = self.font.render("三国帮派模拟", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(self.screen.get_width()/2, 60 * self.scale))
        self.screen.blit(title, title_rect)
        
        # 副标题
        subtitle = self.font.render("请选择游戏模式", True, COLORS['TEXT'])
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width()/2, 90 * self.scale))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 绘制按钮（美化按钮样式）
        for button in self.buttons:
            # 按钮背景
            color = COLORS['HIGHLIGHT'] if button["rect"].collidepoint(pygame.mouse.get_pos()) else (240, 240, 240)
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=int(8 * self.scale))
            pygame.draw.rect(self.screen, COLORS['TEXT'], button["rect"], 
                            width=int(2 * self.scale), border_radius=int(8 * self.scale))
            
            # 按钮文字
            text = self.font.render(button["text"], True, COLORS['TEXT'])
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # 绘制音乐控制按钮
        self.draw_music_button()
        
        pygame.display.flip()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    # 检查是否点击了音乐按钮
                    if self.is_music_button_hovered():
                        self.toggle_music()
                        return True
                    
                    # 检查是否点击了模式按钮
                    for button in self.buttons:
                        if button["rect"].collidepoint(event.pos):
                            self.selected_mode = button["mode"]
                            self.running = False
                            return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                elif event.key == pygame.K_m:
                    # 快捷键切换音乐
                    self.toggle_music()
                    return True
            elif event.type == pygame.VIDEORESIZE:
                # 窗口大小改变时更新
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), 
                    pygame.RESIZABLE
                )
                # 重新计算按钮位置
                button_width = 300 * self.scale
                button_height = 60 * self.scale
                button_y1 = 200 * self.scale
                button_y2 = 300 * self.scale
                
                self.buttons[0]["rect"] = pygame.Rect(
                    (event.w - button_width) / 2, 
                    button_y1, 
                    button_width, 
                    button_height
                )
                self.buttons[1]["rect"] = pygame.Rect(
                    (event.w - button_width) / 2, 
                    button_y2, 
                    button_width, 
                    button_height
                )
                # 更新音乐按钮位置
                self.update_music_button_position()
        return True
    
    def run(self):
        """运行模式选择界面"""
        clock = pygame.time.Clock()
        while self.running:
            if not self.handle_events():
                break
            self.draw()
            clock.tick(10)
        return self.selected_mode

# 模拟主类
class Simulation:
    def __init__(self, game_mode):
        # 游戏模式
        self.game_mode = game_mode
        
        # 初始化天数
        self.day = 0
        
        # 基础尺寸
        self.base_map_width = MAP_SIZE * BASE_CELL_SIZE
        self.base_info_width = BASE_INFO_WIDTH
        self.base_window_width = self.base_map_width + self.base_info_width
        self.base_window_height = MAP_SIZE * BASE_CELL_SIZE
        
        # 缩放相关
        self.scale = INITIAL_SCALE  # 初始缩放比例
        self.min_scale = 0.5  # 最小缩放比例
        self.max_scale = 2.0  # 最大缩放比例
        
        # 创建可调整大小的窗口
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption("三国模拟")
        
        # 初始化地图（50x50）
        self.map_grid = [[None for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]  # 单位位置
        self.land_grid = [[Faction.EMPTY for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]  # 土地所有权
        
        # 定义各派系初始领土位置
        # 魏国在顶部中间
        wei_start_x = (MAP_SIZE - INITIAL_TERRITORY_SIZE) // 2
        wei_start_y = 0
        
        # 蜀国在左下角
        shu_start_x = 0
        shu_start_y = MAP_SIZE - INITIAL_TERRITORY_SIZE
        
        # 吴国在右下角
        wu_start_x = MAP_SIZE - INITIAL_TERRITORY_SIZE
        wu_start_y = MAP_SIZE - INITIAL_TERRITORY_SIZE
        
        # 初始化三个派系，指定初始领土范围
        self.shu = FactionManager(Faction.SHU, shu_start_x, shu_start_y, INITIAL_TERRITORY_SIZE)
        self.wei = FactionManager(Faction.WEI, wei_start_x, wei_start_y, INITIAL_TERRITORY_SIZE)
        self.wu = FactionManager(Faction.WU, wu_start_x, wu_start_y, INITIAL_TERRITORY_SIZE)
        
        # 对于AI自主模式，初始状态更倾向于和平
        if self.game_mode == GameMode.AI_AUTONOMOUS_ALLIANCE:
            self.init_balanced_relations()
        
        # 标记初始领土
        self.mark_initial_territory()
        
        # 将初始单位放置到地图上
        for unit in self.shu.units + self.wei.units + self.wu.units:
            self.map_grid[unit.y][unit.x] = unit
        
        # 更新初始地皮数量
        self.shu.update_land_count(self.land_grid)
        self.wei.update_land_count(self.land_grid)
        self.wu.update_land_count(self.land_grid)
        
        # 记录上一回合的联盟总领地
        self.previous_alliance_land = {}
        
        # 外交请求队列
        self.diplomatic_requests = []
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_font = self._get_scaled_font()
        
        # 音乐控制变量
        self.music_playing = pygame.mixer.music.get_busy()
        
        # 音乐按钮相关
        self.music_button_radius = int(20 * self.scale)
        self.update_music_button_position()

    def update_music_button_position(self):
        """更新音乐按钮位置（右上角）"""
        self.music_button_pos = (
            self.screen.get_width() - self.music_button_radius - 10 * self.scale,
            self.music_button_radius + 10 * self.scale
        )
    
    def init_balanced_relations(self):
        """初始化更平衡的外交关系（模式二）"""
        # 降低初始战争概率，70%概率初始为全部和平
        if random.random() < 0.7:
            pass  # 不记录事件，改用排行榜展示
        else:
            # 30%概率有一对处于战争状态
            war_combinations = [
                (Faction.SHU, Faction.WEI),
                (Faction.WEI, Faction.WU),
                (Faction.WU, Faction.SHU)
            ]
            
            # 随机选择一种组合
            faction1, faction2 = random.choice(war_combinations)
            
            # 设置交战状态
            if faction1 == Faction.SHU:
                self.shu.set_diplomacy_status(Faction.WEI, DiplomaticStatus.WAR)
                self.wei.set_diplomacy_status(Faction.SHU, DiplomaticStatus.WAR)
            elif faction1 == Faction.WEI:
                self.wei.set_diplomacy_status(Faction.WU, DiplomaticStatus.WAR)
                self.wu.set_diplomacy_status(Faction.WEI, DiplomaticStatus.WAR)
            else:  # WU vs SHU
                self.wu.set_diplomacy_status(Faction.SHU, DiplomaticStatus.WAR)
                self.shu.set_diplomacy_status(Faction.WU, DiplomaticStatus.WAR)

    def _get_scaled_font(self):
        """获取按当前缩放比例调整的字体（保持15px基准）"""
        font_size = max(10, int(BASE_FONT_SIZE * self.scale))
        for font_name in font_options:
            try:
                return pygame.font.SysFont(font_name, font_size)
            except:
                continue
        return pygame.font.Font(None, font_size)

    def _update_scale_from_window_size(self, width, height):
        """根据窗口大小更新缩放比例，保持等比例"""
        # 计算基于宽度和高度的可能缩放比例
        scale_by_width = width / self.base_window_width
        scale_by_height = height / self.base_window_height
        
        # 取较小的缩放比例，确保内容不会超出窗口
        new_scale = min(scale_by_width, scale_by_height)
        
        # 限制缩放范围
        self.scale = max(self.min_scale, min(new_scale, self.max_scale))
        
        # 更新字体
        self.current_font = self._get_scaled_font()
        
        # 更新音乐按钮大小和位置
        self.music_button_radius = int(20 * self.scale)
        self.update_music_button_position()

    def mark_initial_territory(self):
        """标记各派系的初始领土"""
        # 标记蜀国初始领土（左下角）
        for y in range(self.shu.start_y, self.shu.start_y + self.shu.size):
            for x in range(self.shu.start_x, self.shu.start_x + self.shu.size):
                if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
                    self.land_grid[y][x] = Faction.SHU
        
        # 标记魏国初始领土（顶部）
        for y in range(self.wei.start_y, self.wei.start_y + self.wei.size):
            for x in range(self.wei.start_x, self.wei.start_x + self.wei.size):
                if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
                    self.land_grid[y][x] = Faction.WEI
        
        # 标记吴国初始领土（右下角）
        for y in range(self.wu.start_y, self.wu.start_y + self.wu.size):
            for x in range(self.wu.start_x, self.wu.start_x + self.wu.size):
                if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
                    self.land_grid[y][x] = Faction.WU
    
    def get_strongest_faction(self):
        """获取当前最强的派系"""
        factions = [self.shu, self.wei, self.wu]
        return max(factions, key=lambda f: f.calculate_strength())
    
    def get_alliances_mode1(self):
        """模式一：确定结盟关系 - 较弱的两个派系结盟对抗最强派系"""
        factions = [self.shu, self.wei, self.wu]
        # 按实力排序
        sorted_factions = sorted(factions, key=lambda f: f.calculate_strength(), reverse=True)
        
        strongest = sorted_factions[0]
        allies = sorted_factions[1:]
        
        # 更新外交状态
        # 最强派系与其他两个派系处于交战状态
        strongest.set_diplomacy_status(allies[0].faction, DiplomaticStatus.WAR)
        strongest.set_diplomacy_status(allies[1].faction, DiplomaticStatus.WAR)
        allies[0].set_diplomacy_status(strongest.faction, DiplomaticStatus.WAR)
        allies[1].set_diplomacy_status(strongest.faction, DiplomaticStatus.WAR)
        
        # 两个较弱派系结盟
        allies[0].set_diplomacy_status(allies[1].faction, DiplomaticStatus.ALLIANCE)
        allies[1].set_diplomacy_status(allies[0].faction, DiplomaticStatus.ALLIANCE)
        
        return strongest, allies
    
    def get_current_alliances(self):
        """获取当前所有联盟关系，返回联盟对列表"""
        factions = [self.shu, self.wei, self.wu]
        alliances = []
        
        for i in range(len(factions)):
            for j in range(i+1, len(factions)):
                if factions[i].is_allied(factions[j].faction):
                    alliances.append((factions[i], factions[j]))
        
        return alliances
    
    def process_diplomacy_mode2(self):
        """处理模式二的外交关系和请求 - 限制最多两个国家联盟，并根据领地变化调整解散几率"""
        factions = [self.shu, self.wei, self.wu]
        
        # 更新联盟持续时间
        for faction in factions:
            faction.update_alliance_turns()
        
        # 获取当前所有联盟
        current_alliances = self.get_current_alliances()
        
        # 处理所有未完成的外交请求
        for request in self.diplomatic_requests[:]:  # 使用副本迭代，以便可以修改原列表
            if request.status != "pending":
                continue
                
            request.turns_pending += 1
            # 如果请求等待太久（超过3天），自动拒绝
            if request.turns_pending > 3:
                request.status = "rejected"
                self.diplomatic_requests.remove(request)
                continue
                
            # AI决定是否接受请求
            acceptance_chance = 0.0
            
            if request.request_type == "结盟":
                # 检查是否已有两个国家联盟，如果是则不能再结盟
                if len(current_alliances) >= 1:
                    # 已有一个联盟，不能再形成新的联盟
                    request.status = "rejected"
                    self.diplomatic_requests.remove(request)
                    continue
                
                # 提高结盟的接受概率
                # 因素1: 与请求方的共同敌人
                common_enemies = 0
                for f in factions:
                    if f != request.sender and f != request.receiver:
                        if (request.sender.is_at_war(f.faction) and 
                            request.receiver.is_at_war(f.faction)):
                            common_enemies += 1
                
                # 有共同敌人时更可能结盟
                common_enemy_factor = 0.3 + (common_enemies * 0.3)
                
                # 因素2: 与最强派系的对比
                strongest = self.get_strongest_faction()
                if (request.sender != strongest and request.receiver != strongest):
                    # 两个较弱派系更可能结盟
                    strength_factor = 0.4
                else:
                    strength_factor = 0.1
                
                # 综合决定接受概率
                acceptance_chance = 0.2 + common_enemy_factor + strength_factor
                
            elif request.request_type == "停战":
                # 被请求方考虑是否接受停战
                # 因素1: 与请求方的实力对比
                sender_strength = request.sender.calculate_strength()
                receiver_strength = request.receiver.calculate_strength()
                strength_factor = min(1.0, sender_strength / receiver_strength) if receiver_strength > 0 else 1.0
                
                # 因素2: 与第三方的关系
                third_faction = None
                for f in factions:
                    if f != request.sender and f != request.receiver:
                        third_faction = f
                        break
                
                if third_faction:
                    if request.receiver.is_at_war(third_faction.faction):
                        # 如果与第三方处于战争，更可能接受停战
                        third_factor = 0.7
                    else:
                        third_factor = 0.3
                else:
                    third_factor = 0.5
                
                # 综合决定接受概率
                acceptance_chance = 0.3 + 0.4 * strength_factor + 0.3 * third_factor
            
            # 确保概率不超过1.0
            acceptance_chance = min(1.0, acceptance_chance)
            
            # 做出决定
            if random.random() < acceptance_chance:
                # 接受请求
                request.status = "accepted"
                
                if request.request_type == "结盟":
                    # 建立联盟关系
                    request.sender.set_diplomacy_status(request.receiver.faction, DiplomaticStatus.ALLIANCE)
                    request.receiver.set_diplomacy_status(request.sender.faction, DiplomaticStatus.ALLIANCE)
                    
                    # 记录初始联盟总领地
                    alliance_key = frozenset([request.sender.faction, request.receiver.faction])
                    self.previous_alliance_land[alliance_key] = request.sender.land + request.receiver.land
                elif request.request_type == "停战":
                    # 建立停战关系
                    request.sender.set_diplomacy_status(request.receiver.faction, DiplomaticStatus.PEACE)
                    request.receiver.set_diplomacy_status(request.sender.faction, DiplomaticStatus.PEACE)
            else:
                # 拒绝请求
                request.status = "rejected"
            
            # 从请求队列中移除已处理的请求
            self.diplomatic_requests.remove(request)
        
        # 检查是否需要发起外交请求
        for faction in factions:
            # 寻找可以结盟的对象
            for other in factions:
                if (faction != other and 
                    not faction.is_allied(other.faction) and 
                    not faction.is_at_war(other.faction)):
                    
                    # 检查是否已经有向该派系的请求
                    has_pending_request = any(
                        r.sender == faction and 
                        r.receiver == other and 
                        r.status == "pending"
                        for r in self.diplomatic_requests
                    )
                    
                    # 检查当前联盟数量，如果已有联盟则不发送新的结盟请求
                    if len(current_alliances) >= 1:
                        continue
                    
                    # 因素1: 是否有共同敌人
                    common_enemies = 0
                    for f in factions:
                        if f != faction and f != other:
                            if faction.is_at_war(f.faction) and other.is_at_war(f.faction):
                                common_enemies += 1
                    
                    # 因素2: 最强派系是否过于强大
                    strongest = self.get_strongest_faction()
                    strength_ratio = strongest.calculate_strength() / max(1, faction.calculate_strength())
                    
                    # 综合概率：有共同敌人或面对强大威胁时更可能请求结盟
                    request_chance = 0.1  # 基础概率
                    if common_enemies > 0:
                        request_chance += 0.2  # 有共同敌人增加概率
                    if strength_ratio > 1.5:
                        request_chance += 0.2  # 最强派系过于强大增加概率
                    
                    # 发送结盟请求
                    if not has_pending_request and random.random() < request_chance:
                        self.diplomatic_requests.append(
                            DiplomaticRequest(faction, other, "结盟")
                        )
        
        # 随机改变一些外交关系
        if random.random() < 0.08:  # 8%的概率发生外交变化
            # 随机选择两个不同的派系
            while True:
                f1, f2 = random.sample(factions, 2)
                if f1 != f2:
                    break
            
            current_status = f1.get_diplomacy_status(f2.faction)
            
            # 联盟持续时间越长，越不容易破裂（基础稳定性）
            alliance_stability = 0
            if current_status == DiplomaticStatus.ALLIANCE:
                # 联盟持续时间越长，基础稳定性越高
                alliance_stability = min(0.8, f1.alliance_turns[f2.faction] * 0.1)
                
                # 根据联盟总领地变化调整稳定性
                alliance_key = frozenset([f1.faction, f2.faction])
                current_alliance_land = f1.land + f2.land
                
                # 检查是否有上一回合的记录
                if alliance_key in self.previous_alliance_land:
                    land_change = current_alliance_land - self.previous_alliance_land[alliance_key]
                    
                    if land_change < 0:
                        # 联盟总领地减少，降低稳定性（增加解散几率）
                        land_factor = -0.4  # 负面因素
                    elif land_change > 0:
                        # 联盟总领地增加，提高稳定性（降低解散几率）
                        land_factor = 0.3  # 正面因素
                    else:
                        land_factor = 0  # 无变化
                else:
                    land_factor = 0
                    # 记录当前联盟领地作为下一回合的参考
                    self.previous_alliance_land[alliance_key] = current_alliance_land
                
                # 更新联盟领地记录
                self.previous_alliance_land[alliance_key] = current_alliance_land
                
                # 综合稳定性 = 基础稳定性 + 领地变化因素
                alliance_stability += land_factor
                # 确保稳定性在合理范围内
                alliance_stability = max(0, min(alliance_stability, 0.9))
            
            # 随机改变状态
            if current_status == DiplomaticStatus.PEACE:
                # 检查是否已有联盟，如果没有则可以结盟
                if len(current_alliances) < 1:
                    # 50%概率结盟
                    if random.random() < 0.5:
                        # 变为联盟
                        f1.set_diplomacy_status(f2.faction, DiplomaticStatus.ALLIANCE)
                        f2.set_diplomacy_status(f1.faction, DiplomaticStatus.ALLIANCE)
                        # 记录初始联盟总领地
                        alliance_key = frozenset([f1.faction, f2.faction])
                        self.previous_alliance_land[alliance_key] = f1.land + f2.land
                    elif random.random() < 0.3:  # 30%概率战争（总体15%）
                        # 变为战争
                        f1.set_diplomacy_status(f2.faction, DiplomaticStatus.WAR)
                        f2.set_diplomacy_status(f1.faction, DiplomaticStatus.WAR)
                else:
                    # 已有联盟，只能考虑战争
                    if random.random() < 0.15:  # 15%概率战争
                        f1.set_diplomacy_status(f2.faction, DiplomaticStatus.WAR)
                        f2.set_diplomacy_status(f1.faction, DiplomaticStatus.WAR)
            
            elif current_status == DiplomaticStatus.WAR:
                # 60%概率停战
                if random.random() < 0.6:
                    f1.set_diplomacy_status(f2.faction, DiplomaticStatus.PEACE)
                    f2.set_diplomacy_status(f1.faction, DiplomaticStatus.PEACE)
            
            elif current_status == DiplomaticStatus.ALLIANCE:
                # 联盟破裂概率受稳定性影响
                # 稳定性越高，破裂概率越低
                break_chance = 0.1 - alliance_stability
                break_chance = max(0.05, min(break_chance, 0.5))  # 确保概率在合理范围内
                
                if random.random() < break_chance:
                    f1.set_diplomacy_status(f2.faction, DiplomaticStatus.PEACE)
                    f2.set_diplomacy_status(f1.faction, DiplomaticStatus.PEACE)
                    # 移除联盟领地记录
                    alliance_key = frozenset([f1.faction, f2.faction])
                    if alliance_key in self.previous_alliance_land:
                        del self.previous_alliance_land[alliance_key]
    
    def generate_new_units(self):
        """根据拥有的地皮和人口限制生成新单位，新单位会在派系现有领土内生成"""
        # 每个派系都有机会生成新单位
        for faction_manager in [self.shu, self.wei, self.wu]:
            # 检查是否已达到兵力上限
            if len(faction_manager.units) >= faction_manager.max_units:
                continue
                
            # 根据地皮数量和人口成本计算最大可能新增单位数
            if not faction_manager.units:
                continue
                
            max_possible_units = faction_manager.land // faction_manager.units[0].population_cost
            # 考虑兵力上限
            max_possible_units = min(max_possible_units, faction_manager.max_units - len(faction_manager.units))
            
            # 有50%的概率实际生成一个单位（如果可能）
            if max_possible_units > 0 and random.random() < 0.5:
                # 在派系现有领土内尝试生成新单位
                attempts = 0
                while attempts < 100:  # 最多尝试100次
                    # 先尝试在初始领土附近生成
                    x = random.randint(
                        max(0, faction_manager.start_x - 5), 
                        min(MAP_SIZE - 1, faction_manager.start_x + faction_manager.size + 5)
                    )
                    y = random.randint(
                        max(0, faction_manager.start_y - 5), 
                        min(MAP_SIZE - 1, faction_manager.start_y + faction_manager.size + 5)
                    )
                    
                    # 如果找不到位置，扩大搜索范围到整个派系领土
                    if attempts > 50 and self.land_grid[y][x] != faction_manager.faction:
                        # 随机找一个派系的领土
                        valid_positions = []
                        for y_coord in range(MAP_SIZE):
                            for x_coord in range(MAP_SIZE):
                                if (self.land_grid[y_coord][x_coord] == faction_manager.faction and 
                                    self.map_grid[y_coord][x_coord] is None):
                                    valid_positions.append((x_coord, y_coord))
                        
                        if valid_positions:
                            x, y = random.choice(valid_positions)
                    
                    if self.map_grid[y][x] is None:
                        # 在这个位置生成新单位
                        new_unit = faction_manager.add_unit(x, y, self.land_grid)
                        if new_unit:  # 只有在成功添加时才更新地图
                            self.map_grid[y][x] = new_unit
                        break
                        
                    attempts += 1
    
    def move_units(self):
        """移动所有单位并更新土地所有权，单位更倾向于向未占领区域移动"""
        # 获取派系关系信息
        if self.game_mode == GameMode.TWO_WEAK_AGAINST_STRONG:
            strongest, allies = self.get_alliances_mode1()
        
        # 遍历所有单位并移动
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                unit = self.map_grid[y][x]
                if unit is None:
                    continue
                
                # 保存原位置
                original_x, original_y = unit.x, unit.y
                
                # 决定移动方向 - 倾向于向未占领区域或敌对区域移动
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上下左右
                preferred_dirs = []
                avoid_dirs = []
                
                # 检查各个方向的情况
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                        # 检查该位置的派系
                        if self.land_grid[ny][nx] == Faction.EMPTY:
                            preferred_dirs.append((dx, dy))
                        else:
                            # 检查是否是敌对派系的领土
                            is_enemy = False
                            
                            if self.game_mode == GameMode.TWO_WEAK_AGAINST_STRONG:
                                # 模式一：对抗最强派系
                                if (unit.faction == strongest.faction and 
                                    self.land_grid[ny][nx] in [a.faction for a in allies]):
                                    is_enemy = True
                                elif (unit.faction in [a.faction for a in allies] and 
                                      self.land_grid[ny][nx] == strongest.faction):
                                    is_enemy = True
                            else:
                                # 模式二：根据外交关系判断
                                if unit.faction == Faction.SHU:
                                    is_enemy = self.shu.is_at_war(self.land_grid[ny][nx])
                                elif unit.faction == Faction.WEI:
                                    is_enemy = self.wei.is_at_war(self.land_grid[ny][nx])
                                else:  # WU
                                    is_enemy = self.wu.is_at_war(self.land_grid[ny][nx])
                            
                            if is_enemy:
                                preferred_dirs.append((dx, dy))
                            elif self.land_grid[ny][nx] != unit.faction:
                                # 是盟友或中立派系，避免移动
                                avoid_dirs.append((dx, dy))
                
                # 选择移动方向
                dx, dy = 0, 0
                if random.random() < 0.7:  # 70%的概率移动
                    if preferred_dirs:  # 如果有偏好方向（未占领区域或敌对区域），优先选择
                        dx, dy = random.choice(preferred_dirs)
                    else:
                        # 从非避免方向中选择
                        possible_dirs = [d for d in directions if d not in avoid_dirs]
                        if possible_dirs:
                            dx, dy = random.choice(possible_dirs)
                        else:
                            dx, dy = random.choice(directions)
                
                # 尝试移动
                moved = unit.move(dx, dy, self.map_grid, self.land_grid)
                
                # 如果移动了，更新地图
                if moved:
                    self.map_grid[original_y][original_x] = None
                    self.map_grid[unit.y][unit.x] = unit
                    
                    # 移动后，周围的土地也会被该派系影响
                    self.influence_territory(unit.x, unit.y, unit.faction)
    
    def influence_territory(self, x, y, faction):
        """单位移动后，影响周围的土地"""
        # 影响周围3x3的格子
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:  # 跳过自身位置
                    continue
                    
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    # 空地不需要检查盟友关系，直接尝试影响
                    if self.land_grid[ny][nx] == Faction.EMPTY:
                        # 调整影响力，使各派系更平衡
                        if faction == Faction.SHU:  # 现在是矮人属性
                            influence_chance = 0.25  # 原魏国的土地影响力
                        elif faction == Faction.WEI:  # 现在是巨人属性
                            influence_chance = 0.3  # 原蜀国的土地影响力
                        else:  # WU
                            influence_chance = 0.28  # 吴国中间
                            
                        if random.random() < influence_chance:
                            self.land_grid[ny][nx] = faction
                    else:
                        # 检查是否是盟友领土，如果是则不影响
                        is_ally = False
                        
                        if faction == Faction.SHU:
                            is_ally = self.shu.is_allied(self.land_grid[ny][nx])
                        elif faction == Faction.WEI:
                            is_ally = self.wei.is_allied(self.land_grid[ny][nx])
                        else:  # WU
                            is_ally = self.wu.is_allied(self.land_grid[ny][nx])
                        
                        if not is_ally:
                            # 调整影响力，使各派系更平衡
                            if faction == Faction.SHU:  # 现在是矮人属性
                                influence_chance = 0.25  # 原魏国的土地影响力
                            elif faction == Faction.WEI:  # 现在是巨人属性
                                influence_chance = 0.3  # 原蜀国的土地影响力
                            else:  # WU
                                influence_chance = 0.28  # 吴国中间
                                
                            if random.random() < influence_chance:
                                self.land_grid[ny][nx] = faction
    
    def handle_combat(self):
        """处理单位之间的战斗，胜利者获得土地，攻击范围为周围6个方向"""
        # 获取派系关系信息
        if self.game_mode == GameMode.TWO_WEAK_AGAINST_STRONG:
            strongest, allies = self.get_alliances_mode1()
        
        # 记录要移除的单位（避免在遍历中修改列表）
        units_to_remove = []
        # 记录已经攻击过的单位对，避免重复攻击
        attacked_pairs = set()
        
        # 检查单位之间的战斗，攻击范围为周围6个方向（上下左右和两个对角线）
        attack_directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]  # 六个方向
        
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                unit = self.map_grid[y][x]
                if unit is None or unit in units_to_remove:
                    continue
                
                # 检查六个方向的单位
                for dx, dy in attack_directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                        enemy = self.map_grid[ny][nx]
                        if enemy is not None and enemy not in units_to_remove:
                            # 判断是否为敌对关系
                            is_hostile = False
                            
                            if self.game_mode == GameMode.TWO_WEAK_AGAINST_STRONG:
                                # 模式一：两弱联合抗强
                                if (unit.faction == strongest.faction and 
                                    enemy.faction in [a.faction for a in allies]):
                                    is_hostile = True
                                elif (enemy.faction == strongest.faction and 
                                      unit.faction in [a.faction for a in allies]):
                                    is_hostile = True
                            else:
                                # 模式二：根据外交关系判断
                                if unit.faction == Faction.SHU:
                                    is_hostile = self.shu.is_at_war(enemy.faction)
                                elif unit.faction == Faction.WEI:
                                    is_hostile = self.wei.is_at_war(enemy.faction)
                                else:  # WU
                                    is_hostile = self.wu.is_at_war(enemy.faction)
                            
                            if is_hostile:
                                # 确保每个战斗只处理一次
                                pair_key = frozenset([(unit.x, unit.y, unit.faction), 
                                                    (enemy.x, enemy.y, enemy.faction)])
                                if pair_key in attacked_pairs:
                                    continue
                                attacked_pairs.add(pair_key)
                                
                                # 处理战斗
                                self.resolve_battle(unit, enemy, units_to_remove)
        
        return units_to_remove
    
    def resolve_battle(self, attacker, defender, units_to_remove):
        """处理两个单位之间的战斗"""
        # 攻击者先攻击
        defender_destroyed = attacker.attack_unit(defender)
        if defender_destroyed and defender not in units_to_remove:
            units_to_remove.append(defender)
            return  # 防御者已被消灭，无法反击
        
        # 防御者反击
        attacker_destroyed = defender.attack_unit(attacker)
        if attacker_destroyed and attacker not in units_to_remove:
            units_to_remove.append(attacker)
    
    def update(self):
        """更新模拟状态"""
        self.day += 1
        
        # 更新地皮数量
        self.shu.update_land_count(self.land_grid)
        self.wei.update_land_count(self.land_grid)
        self.wu.update_land_count(self.land_grid)
        
        # 模式一：更新联盟关系
        if self.game_mode == GameMode.TWO_WEAK_AGAINST_STRONG:
            self.get_alliances_mode1()
        
        # 模式二：处理外交关系
        if self.game_mode == GameMode.AI_AUTONOMOUS_ALLIANCE:
            self.process_diplomacy_mode2()
        
        # 生成新单位
        self.generate_new_units()
        
        # 移动单位
        self.move_units()
        
        # 处理战斗
        units_to_remove = self.handle_combat()
        
        # 移除战斗中被消灭的单位，并更新土地所有权
        for unit in units_to_remove:
            # 胜利者获得该土地
            self.land_grid[unit.y][unit.x] = None  # 先清空
            
            # 寻找附近的胜利者
            winner = None
            attack_directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]
            for dx, dy in attack_directions:
                nx, ny = unit.x + dx, unit.y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    potential_winner = self.map_grid[ny][nx]
                    if potential_winner is not None and potential_winner != unit:
                        winner = potential_winner
                        break
            
            # 如果找到胜利者，将土地分配给胜利者派系
            if winner:
                self.land_grid[unit.y][unit.x] = winner.faction
            else:
                # 如果没有胜利者，标记为空地
                self.land_grid[unit.y][unit.x] = Faction.EMPTY
                
            # 从地图上移除单位
            self.map_grid[unit.y][unit.x] = None
            if unit.faction == Faction.SHU:
                self.shu.remove_unit(unit)
            elif unit.faction == Faction.WEI:
                self.wei.remove_unit(unit)
            elif unit.faction == Faction.WU:
                self.wu.remove_unit(unit)
    
    def draw_music_button(self):
        """绘制音乐控制按钮（右上角）"""
        # 按钮背景
        color = COLORS['MUSIC_BUTTON_HIGHLIGHT'] if self.is_music_button_hovered() else COLORS['MUSIC_BUTTON']
        pygame.draw.circle(
            self.screen, 
            color, 
            (int(self.music_button_pos[0]), int(self.music_button_pos[1])), 
            self.music_button_radius
        )
        pygame.draw.circle(
            self.screen, 
            COLORS['TEXT'], 
            (int(self.music_button_pos[0]), int(self.music_button_pos[1])), 
            self.music_button_radius, 
            2  # 边框宽度
        )
        
        # 绘制音乐图标
        music_icon = "🎵"
        text_surface = self.current_font.render(music_icon, True, COLORS['TEXT'])
        text_rect = text_surface.get_rect(center=self.music_button_pos)
        self.screen.blit(text_surface, text_rect)
        
        # 如果音乐暂停，显示暂停指示
        if not self.music_playing:
            # 绘制一个简单的暂停符号
            bar_width = int(self.music_button_radius * 0.3)
            bar_height = int(self.music_button_radius * 0.6)
            bar1_x = self.music_button_pos[0] - bar_width - int(self.scale * 2)
            bar2_x = self.music_button_pos[0] + int(self.scale * 2)
            
            pygame.draw.rect(
                self.screen, 
                (200, 0, 0),  # 红色指示暂停
                (bar1_x, self.music_button_pos[1] - bar_height // 2, 
                 bar_width, bar_height)
            )
            pygame.draw.rect(
                self.screen, 
                (200, 0, 0),  # 红色指示暂停
                (bar2_x, self.music_button_pos[1] - bar_height // 2, 
                 bar_width, bar_height)
            )
    
    def is_music_button_hovered(self):
        """检查鼠标是否悬停在音乐按钮上"""
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.music_button_pos[0]
        dy = mouse_pos[1] - self.music_button_pos[1]
        distance = (dx**2 + dy**2)** 0.5
        return distance <= self.music_button_radius
    
    def toggle_music(self):
        """切换音乐播放状态"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
    
    def draw(self):
        """绘制游戏状态，包括各国占领的地图和信息面板（含国家实力排行榜）"""
        self.screen.fill(COLORS['BACKGROUND'])
        
        # 计算当前尺寸
        current_width, current_height = self.screen.get_size()
        map_width = int(self.base_map_width * self.scale)
        info_width = int(self.base_info_width * self.scale)
        
        # 确保信息面板有足够宽度
        if current_width - map_width < info_width * 0.8:
            map_width = current_width - int(info_width * 0.8)
        
        # 计算单元格大小（按比例缩放）
        scaled_cell_size = map_width / MAP_SIZE
        
        # 绘制地图和土地所有权
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                rect = pygame.Rect(
                    x * scaled_cell_size, 
                    y * scaled_cell_size, 
                    scaled_cell_size, 
                    scaled_cell_size
                )
                unit = self.map_grid[y][x]
                land_owner = self.land_grid[y][x]
                
                # 绘制土地颜色
                if land_owner == Faction.SHU:
                    land_color = COLORS['SHU_LAND']
                elif land_owner == Faction.WEI:
                    land_color = COLORS['WEI_LAND']
                elif land_owner == Faction.WU:
                    land_color = COLORS['WU_LAND']
                else:
                    land_color = COLORS['EMPTY']
                
                pygame.draw.rect(self.screen, land_color, rect)
                
                # 如果有单位，在土地上绘制单位
                if unit is not None:
                    # 根据单位类型选择颜色（特别是吴国的精英单位）
                    if unit.faction == Faction.SHU:
                        unit_color = COLORS['SHU']
                    elif unit.faction == Faction.WEI:
                        unit_color = COLORS['WEI']
                    else:  # WU
                        # 棒球棍大哥使用更深的颜色
                        unit_color = COLORS['WU_ELITE'] if unit.unit_type == "棒球棍大哥" else COLORS['WU']
                    
                    # 绘制单位（比土地小一点的方块）
                    border = max(1, int(scaled_cell_size * 0.1))  # 边框大小随缩放调整
                    unit_rect = pygame.Rect(
                        x * scaled_cell_size + border, 
                        y * scaled_cell_size + border, 
                        scaled_cell_size - 2 * border, 
                        scaled_cell_size - 2 * border
                    )
                    pygame.draw.rect(self.screen, unit_color, unit_rect)
                
                # 绘制网格线（线宽随缩放调整）
                line_width = max(1, int(scaled_cell_size * 0.05))
                pygame.draw.rect(self.screen, (100, 100, 100), rect, line_width)
        
        # 绘制信息面板边框
        info_panel_rect = pygame.Rect(
            map_width, 
            0, 
            current_width - map_width, 
            current_height
        )
        pygame.draw.rect(self.screen, COLORS['PANEL_BORDER'], info_panel_rect, int(2 * self.scale))
        
        # 绘制信息面板内容
        info_x = map_width + 15 * self.scale  # 增加内边距
        info_y = 15 * self.scale
        line_spacing = 22 * self.scale  # 行间距（优化为更紧凑）
        
        # 绘制标题栏（游戏模式）
        title_bg_rect = pygame.Rect(
            map_width, 
            0, 
            current_width - map_width, 
            40 * self.scale
        )
        pygame.draw.rect(self.screen, COLORS['PANEL_HEADER'], title_bg_rect)
        pygame.draw.line(
            self.screen, 
            COLORS['SEPARATOR'], 
            (map_width, 40 * self.scale), 
            (current_width, 40 * self.scale), 
            int(1 * self.scale)
        )
        
        mode_text = self.current_font.render(f"模式: {self.game_mode.value}", True, COLORS['TEXT'])
        self.screen.blit(mode_text, (info_x, 15 * self.scale))
        
        # 调整信息起始位置到标题栏下方
        info_y = 50 * self.scale
        
        # 绘制天数
        day_text = self.current_font.render(f"天数: {self.day}", True, COLORS['TEXT'])
        self.screen.blit(day_text, (info_x, info_y))
        info_y += line_spacing
        
        # 显示音乐状态
        music_status = "音乐: 播放中" if self.music_playing else "音乐: 已暂停"
        music_text = self.current_font.render(music_status, True, COLORS['TEXT'])
        self.screen.blit(music_text, (info_x, info_y))
        info_y += line_spacing
        
        # 绘制分隔线
        pygame.draw.line(
            self.screen, 
            COLORS['SEPARATOR'], 
            (info_x - 5 * self.scale, info_y + 5 * self.scale), 
            (current_width - 10 * self.scale, info_y + 5 * self.scale), 
            int(1 * self.scale)
        )
        info_y += line_spacing * 1.2
        
        # 绘制各派系信息
        factions = [self.shu, self.wei, self.wu]
        for i, faction in enumerate(factions):
            if faction.faction == Faction.SHU:
                color = COLORS['SHU']
            elif faction.faction == Faction.WEI:
                color = COLORS['WEI']
            else:
                color = COLORS['WU']
                
            strength = faction.calculate_strength()
            
            # 绘制派系名称和颜色块
            color_block_size = int(18 * self.scale)
            pygame.draw.rect(self.screen, color, (info_x, info_y, color_block_size, color_block_size))
            name_text = self.current_font.render(f"{faction.faction.value}国", True, COLORS['TEXT'])
            self.screen.blit(name_text, (info_x + color_block_size + 10 * self.scale, info_y))
            info_y += line_spacing
            
            # 绘制单位数量（显示当前/上限）
            units_text = self.current_font.render(
                f"单位数量: {len(faction.units)}/{faction.max_units}", 
                True, COLORS['TEXT']
            )
            self.screen.blit(units_text, (info_x + 10 * self.scale, info_y))
            info_y += line_spacing
            
            # 绘制地皮数量
            land_text = self.current_font.render(f"地皮数量: {faction.land}", True, COLORS['TEXT'])
            self.screen.blit(land_text, (info_x + 10 * self.scale, info_y))
            info_y += line_spacing
            
            # 绘制人口数量
            pop_text = self.current_font.render(f"人口数量: {faction.population}", True, COLORS['TEXT'])
            self.screen.blit(pop_text, (info_x + 10 * self.scale, info_y))
            info_y += line_spacing
            
            # 绘制实力
            strength_text = self.current_font.render(f"实力: {strength}", True, COLORS['TEXT'])
            self.screen.blit(strength_text, (info_x + 10 * self.scale, info_y))
            info_y += line_spacing
            
            # 显示外交关系
            for other in factions:
                if other != faction:
                    status = faction.get_diplomacy_status(other.faction)
                    dipl_text = self.current_font.render(
                        f"与{other.faction.value}国: {status.value}", 
                        True, COLORS['TEXT']
                    )
                    self.screen.blit(dipl_text, (info_x + 10 * self.scale, info_y))
                    info_y += line_spacing
            
            # 派系之间添加分隔线（最后一个派系不加）
            if i < len(factions) - 1:
                pygame.draw.line(
                    self.screen, 
                    COLORS['SEPARATOR'], 
                    (info_x - 5 * self.scale, info_y + 5 * self.scale), 
                    (current_width - 10 * self.scale, info_y + 5 * self.scale), 
                    int(1 * self.scale)
                )
                info_y += line_spacing * 0.8  # 派系之间增加一些间距
        
        # 绘制实力排行榜标题
        pygame.draw.line(
            self.screen, 
            COLORS['SEPARATOR'], 
            (info_x - 5 * self.scale, info_y + 5 * self.scale), 
            (current_width - 10 * self.scale, info_y + 5 * self.scale), 
            int(1 * self.scale)
        )
        info_y += line_spacing * 1.2
        
        ranking_title = self.current_font.render("国家实力排行榜:", True, COLORS['TEXT'])
        self.screen.blit(ranking_title, (info_x, info_y))
        info_y += line_spacing * 1.2
        
        # 按实力排序派系
        ranked_factions = sorted(factions, key=lambda f: f.calculate_strength(), reverse=True)
        
        # 显示排名（带奖牌图标）
        for i, faction in enumerate(ranked_factions):
            # 排名图标（金、银、铜）
            rank_color = COLORS['RANK_1'] if i == 0 else COLORS['RANK_2'] if i == 1 else COLORS['RANK_3']
            pygame.draw.circle(
                self.screen, 
                rank_color, 
                (int(info_x + 12 * self.scale), int(info_y + 10 * self.scale)), 
                int(10 * self.scale)
            )
            pygame.draw.circle(
                self.screen, 
                (100, 100, 100), 
                (int(info_x + 12 * self.scale), int(info_y + 10 * self.scale)), 
                int(10 * self.scale), 
                int(1 * self.scale)
            )
            
            # 排名文本
            if faction.faction == Faction.SHU:
                text_color = COLORS['SHU']
            elif faction.faction == Faction.WEI:
                text_color = COLORS['WEI']
            else:
                text_color = COLORS['WU']
                
            rank_text = self.current_font.render(
                f"{faction.faction.value}国 - 实力: {faction.calculate_strength()}", 
                True, text_color
            )
            self.screen.blit(rank_text, (info_x + 30 * self.scale, info_y))
            info_y += line_spacing
        
        # 绘制操作说明区域
        pygame.draw.line(
            self.screen, 
            COLORS['SEPARATOR'], 
            (info_x - 5 * self.scale, info_y + 5 * self.scale), 
            (current_width - 10 * self.scale, info_y + 5 * self.scale), 
            int(1 * self.scale)
        )
        info_y += line_spacing * 1.2
        
        # 操作说明
        help_text1 = self.current_font.render("空格键: 单步执行", True, COLORS['TEXT'])
        help_text2 = self.current_font.render("Enter键: 自动运行", True, COLORS['TEXT'])
        help_text3 = self.current_font.render("M键: 切换音乐", True, COLORS['TEXT'])
        help_text4 = self.current_font.render("ESC键: 退出游戏", True, COLORS['TEXT'])
        
        self.screen.blit(help_text1, (info_x, info_y))
        info_y += line_spacing
        self.screen.blit(help_text2, (info_x, info_y))
        info_y += line_spacing
        self.screen.blit(help_text3, (info_x, info_y))
        info_y += line_spacing
        self.screen.blit(help_text4, (info_x, info_y))
        
        # 绘制音乐控制按钮
        self.draw_music_button()
        
        pygame.display.flip()
    
    def run(self):
        """运行模拟"""
        auto_run = False
        
        while self.running:
            # 重置战斗相关变量
            units_to_remove = []
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        # 单步执行
                        self.update()
                    elif event.key == pygame.K_RETURN:
                        # 切换自动运行模式
                        auto_run = not auto_run
                    elif event.key == pygame.K_m:
                        # 切换音乐播放/暂停
                        self.toggle_music()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        # 检查是否点击了音乐按钮
                        if self.is_music_button_hovered():
                            self.toggle_music()
                elif event.type == pygame.VIDEORESIZE:
                    # 窗口大小改变时更新缩放比例，保持等比例
                    self._update_scale_from_window_size(event.w, event.h)
                    # 调整窗口大小
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), 
                        pygame.RESIZABLE
                    )
            
            # 如果自动运行模式开启，更新模拟
            if auto_run:
                self.update()
            
            # 绘制当前状态
            self.draw()
            self.clock.tick(10)  # 限制帧率
        
        pygame.quit()
        sys.exit()

# 运行游戏
if __name__ == "__main__":
    # 创建初始屏幕用于模式选择
    initial_screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )
    
    # 尝试播放背景音乐
    music_played = play_background_music()
    if not music_played:
        print("警告: 无法播放背景音乐，请确保1.flac文件存在于当前目录")
    
    # 显示模式选择界面
    mode_selector = ModeSelection(initial_screen, INITIAL_SCALE)
    selected_mode = mode_selector.run()
    
    if selected_mode:
        # 运行选择的模式
        simulation = Simulation(selected_mode)
        simulation.run()
    else:
        pygame.quit()
        sys.exit()
    
