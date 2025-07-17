# Copyright © 2025 mtmatt, ouo. All rights reserved.

import time
from api import GameClient, GameStatus, Vector2, TowerType, TargetStrategy, EnemyType, SpellType, TerrainType, ChatSource
import math
agent = GameClient(7749, "a47973b5")  # Replace with your token

print("Waiting for game to RUNNING...")
while agent.get_game_status() != GameStatus.RUNNING:
    time.sleep(0.5)
print("Game RUNNING!\n")

agent.set_chat_name_color("7fffd4")
agent.set_name("poyo")
start = time.time()
placed_dk = set()

# 1. 地形
# this need to be flipped and turn clockwise
terrain = agent.get_all_terrain()
'''
for row in terrain:
    for t in row:
        print(f"{t.value:2d}", end=" ")
    print()
'''

# fly path
fly_path = agent.get_system_path(True)


def find_best_donkey_kong_position(terrain, min_road_tiles=8):
    """
    Find all possible DK tower spots using a 4x4 range.

    :param terrain: result of agent.get_all_terrain()
    :param min_road_tiles: minimum roads required to consider a tile
    :return: list of tuples (Vector2, road_count), sorted descending
    """

    rows = len(terrain)
    cols = len(terrain[0])

    spots = []

    for r in range(rows):
        for c in range(cols):
            if terrain[r][c] != TerrainType.EMPTY:
                continue

            road_count = 0

            for dr in range(-2, 3):  # -2 to +2
                for dc in range(-2, 3):
                    nr = r + dr
                    nc = c + dc

                    if 0 <= nr < rows and 0 <= nc < cols:
                        if terrain[nr][nc] == TerrainType.ROAD:
                            road_count += 1

            if road_count >= min_road_tiles:
                spots.append((Vector2(r, c), road_count))

    # Sort by highest road count
    spots.sort(key=lambda x: x[1], reverse=True)

    return spots


def find_corner(terrain):

    # direction definition

    DIRS = [
        (-1, 0),  # up
        (1, 0),   # down
        (0, -1),  # left
        (0, 1),  # right
    ]
    # Find corners. ex DIRS[0] + DIRS[2] = up + left
    CORNER_PAIRS = [
        (0, 2),  # up + left
        (0, 3),  # up + right
        (1, 2),  # down + left
        (1, 3),  # down + right
    ]
    corner_positions = []

    rows = len(terrain)
    cols = len(terrain[0])

    for row in range(rows):
        for col in range(cols):
            if terrain[row][col] == TerrainType.EMPTY:
                for a, b in CORNER_PAIRS:
                    row_a, col_a = row + DIRS[a][0], col + DIRS[a][1]
                    row_b, col_b = row + DIRS[b][0], col + DIRS[b][1]

                    # Check bounds
                    if not (0 <= row_a < rows and 0 <= col_a < cols):
                        continue
                    if not (0 <= row_b < rows and 0 <= col_b < cols):
                        continue

                    if (terrain[row_a][col_a] == TerrainType.ROAD and
                            terrain[row_b][col_b] == TerrainType.ROAD):
                        corner_positions.append(Vector2(row, col))
                        break  # No need to check other pairs
    # Check single terrain and corner positions
    # print("Single terrain at (0,0):", agent.get_terrain(Vector2(0, 0)), "\n")
    # X is down, Y is right
    # print("\nCorners found:")
    # for pos in corner_positions:
    # print(f"Corner at: ({pos.x}, {pos.y})")
    return corner_positions


def place_mario_for_flyers(agent, terrain, fly_path, level="3", num_towers=3):
    """
    Places FIRE_MARIO towers along the flying path, starting from the back.

    :param agent: GameClient instance
    :param level: Mario tower level, e.g. "1", "2a"
    :param num_towers: how many towers to place
    """

    fly_path = agent.get_system_path(True)
    fly_path_reversed = fly_path[::-1]

    placed = 0

    for pos in fly_path_reversed:
        terrain_type = agent.get_terrain(pos)

        if terrain_type == TerrainType.EMPTY:
            tower = agent.get_tower(True, pos)
            if tower is None:
                agent.place_tower(TowerType.FIRE_MARIO, "2a", pos)
                print(
                    f"Placed FIRE_MARIO level {level} at {pos} (air defense).")
                placed += 1

            if placed >= num_towers:
                break
                placed = 0

    if placed == 0:
        print("No suitable tiles found to place FIRE_MARIO towers.")


# find corners
corner_positions = find_corner(terrain)


# print("Flying enemy path:")

# for coord in fly_path:
#    print(f"({coord.x}, {coord.y})")


flyers_last_check_time = 0
koopa_last_check_time = 0
while True:  # 主遊戲
    remain_time = agent.get_remain_time()
    now = time.time()  # 紀錄現在時間

    # dk best position
    terrain = agent.get_all_terrain()
    dk_spots = find_best_donkey_kong_position(terrain)
    print(dk_spots)

    # monster spawn
    if now - koopa_last_check_time >= 2:  # 每2秒召喚一次 "票"寶寶
        agent.spawn_unit(EnemyType.GOOMBA)
        koopa_last_check_time = now
    # spell db cast
    DOUBLE_INCOME_first_usage = False
    if start == 43:
        agent.cast_spell(SpellType.DOUBLE_INCOME)
        agent.send_chat('兩倍錢>:)')
        DOUBLE_INCOME_first_usage = True
    if agent.get_spell_cooldown(True, SpellType.DOUBLE_INCOME) == 0 and DOUBLE_INCOME_first_usage == True:  # 兩倍錢
        agent.cast_spell(SpellType.DOUBLE_INCOME)
        agent.send_chat('兩倍錢>:)')

    if agent.get_money(True) >= 1200:
        for pos in dk_spots:
            if agent.get_tower(True, pos[0]) is None:
                print(f"Placing DK at {pos[0]}")
                agent.place_tower(TowerType.DONKEY_KONG, '2a', pos[0])
                agent.send_chat('放置lv 2 DK')
                placed_dk.add((pos, '2'))
                dk_spots.remove(pos)
                break

    """
以下邏輯解釋
    當錢大於1200 且有效位置還有剩 :
         如果錢大於2800:直接升級lv3b升級lv2
         將座標及等級存入 placed_gorilla 裡 (升級時會用到)
        砲台邏輯一樣
    """
    # balance值:每個砲臺升一級，balance值加一，大於三時則會開始升級猩猩
    if agent.get_money(True) >= 2900 and len(placed_dk) != 0:
        temp = placed_dk.pop()
        agent.send_chat('放置lv 3猩猩')
        agent.place_tower(TowerType.DONKEY_KONG, '3a', temp[0])

    # check the number of flying enemies
    if now - flyers_last_check_time >= 6:
        flyers_last_check_time = now
        # get all flying enemies
        all_enemies = agent.get_all_enemies(True)
        flyers = [e for e in all_enemies if e.flying]
        num_flyers = len(flyers)
        if num_flyers > 3:
            # place mario for flyers
            place_mario_for_flyers(agent, terrain, fly_path)


# 2. 分數、金錢、收入
print("Scores:", agent.get_scores(True),
      "(Me) /", agent.get_scores(False), "(Opp)")
print("Money: ", agent.get_money(True),
      "(Me) /", agent.get_money(False), "(Opp)")
print("Income:", agent.get_income(True), "(Me) /",
      agent.get_income(False), "(Opp)\n")
'''
# 3. 波次與時間
print("Wave:", agent.get_current_wave())
print("Remain time:", f"{agent.get_remain_time():.2f}s")
print("Until next wave:", f"{agent.get_time_until_next_wave():.2f}s\n")

# 4. 路徑
print("System path (ground):", [(c.x, c.y)
      for c in agent.get_system_path(False)])
print("Opponent path (air):",  [(c.x, c.y)
      for c in agent.get_opponent_path(True)], "\n")

# 5. 塔操作
pos = Vector2(5, 5)
if agent.get_tower(True, pos) is None:
    print("No tower at", pos, "→ placing FIRE_MARIO lvl 1")
    agent.place_tower(TowerType.FIRE_MARIO, "1", pos)
print("All my towers:", agent.get_all_towers(True))
# 設定塔的攻擊模式
agent.set_strategy(pos, TargetStrategy.CLOSE)

if agent.get_tower(True, Vector2(1, 2)) is None:
    agent.place_tower(TowerType.ICE_LUIGI, "1", pos)
time.sleep(3)
# 賣塔
agent.sell_tower(Vector2(1, 1))
print("After sell:", agent.get_all_towers(True), "\n")

# 6. 出兵
agent.spawn_unit(EnemyType.KOOPA_PARATROOPA)
print("Opp enemies:", agent.get_all_enemies(False))
print("KOOPA cooldown:",
      f"{agent.get_unit_cooldown(EnemyType.KOOPA_PARATROOPA):.2f}s\n")

# 7. 法術
agent.cast_spell(SpellType.POISON, Vector2(3, 3))
print("My POISON CD:",
      f"{agent.get_spell_cooldown(True, SpellType.POISON):.2f}s\n")

# 8. 聊天
agent.set_name("OuO")
agent.set_chat_name_color("DCB5FF")
sent = agent.send_chat("OuO love you ! <3")
history = agent.get_chat_history(5)
for src, msg in history:
    if src == ChatSource.PLAYER_SELF:
        who = "OuO"
    elif src == ChatSource.PLAYER_OTHER:
        who = "Loser"
    else:
        who = "System"
    print(f"[{who}]", msg)
print()


while True:
    remain_time = agent.get_remain_time()

    # CAST DOUBLE INCOME
    income_multiplier: int = 1
    agent.cast_spell(SpellType.DOUBLE_INCOME)
    income_multiplier = 2

    # INCOME ENHANCEMENT
    if agent.get_income(True) / income_multiplier < 150:
        agent.spawn_unit(EnemyType.GOOMBA)
    elif len(agent.get_all_towers(True)) > 20 and agent.get_income(True) / income_multiplier < 250:
        agent.spawn_unit(EnemyType.GOOMBA)

    # DEFENSE
    terrain = agent.get_all_terrain()
    for (row, data) in enumerate(terrain):
        for (col, tile) in enumerate(data):
            if tile == TerrainType.EMPTY:
                agent.place_tower(TowerType.FIRE_MARIO, '1', Vector2(row, col))

    # ATTACK
    if agent.get_money(True) >= 3000:
        agent.spawn_unit(EnemyType.KOOPA_JR)

    # CHAT
    agent.send_chat('你說飛行敵人太強，其實是你太習慣凡事都想一步解決。')

    agent.send_chat('')

    agent.send_chat('')

    agent.send_chat('')

    agent.send_chat('')
'''
