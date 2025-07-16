# Copyright © 2025 mtmatt. All rights reserved.

import api

agent = api.GameClient(7749, '6ad4da8e')
#    右  左  下 上
dx = [1, -1, 0, 0]
dy = [0, 0, 1, -1]
bomb_tower = []
corner = []
placed_bomb = set()
placed_gorilla = set()
balance = 0
terrain = agent.get_all_terrain()
rows = len(terrain)
cols = len(terrain[0])
agent.set_chat_name_color("7fffd4")
agent.set_name("qhx338")
for row in range(rows):
    for col in range(cols):
        if terrain[row][col] == api.TerrainType.EMPTY:

            for k in range(4):
                count = 0
                temp_row = row
                temp_col = col

                next_row = temp_row + dx[k]
                next_col = temp_col + dy[k]

                while (terrain[next_row][next_col] == api.TerrainType.ROAD):
                    next_row += dx[k]
                    next_col += dy[k]
                    if not (0 <= next_row < rows and 0 <= next_col < cols):
                        break
                    count += 1

                if count >= 5:
                    if terrain[next_row][next_col] == api.TerrainType.OUT_OF_BOUNDS and terrain[next_row][next_col] == api.TerrainType.OBSTACLE:
                       bomb_tower.append(api.Vector2(next_row, next_col))
                    bomb_tower.append(api.Vector2(temp_row, temp_col))
        road_dirs = []
        for k in range(4):
            nr = row + dx[k]
            nc = col + dy[k]

            if 0 <= nr < rows and 0 <= nc < cols and terrain[nr][nc] == api.TerrainType.ROAD:
                road_dirs.append(k)
        is_corner = False
        for a in range(len(road_dirs)):
            for b in range(a + 1, len(road_dirs)):
                d1 = road_dirs[a]
                d2 = road_dirs[b]
                if abs(d1 - d2) % 2 == 1:  # 差1或3表示直角，不是對向
                    is_corner = True
                    break
            if is_corner:
                break

        if is_corner:
            corner.append(api.Vector2(row, col))
pixel_cat = agent.pixelcat()
agent.send_chat(pixel_cat)
while True:
    remain_time = agent.get_remain_time()

    if agent.get_spell_cooldown(True, api.SpellType.DOUBLE_INCOME) == 0:
        agent.cast_spell(api.SpellType.DOUBLE_INCOME)
        agent.send_chat('兩倍錢>:)')

    if agent.get_money(True) >= 400 and bomb_tower:
        agent.place_tower(api.TowerType.FORT, '1', bomb_tower[0])
        agent.send_chat('放置lv 1砲塔')
        placed_bomb.add((bomb_tower[0], '1'))
        del bomb_tower[0]

    elif agent.get_money(True) >= 400 and corner:
        agent.place_tower(api.TowerType.DONKEY_KONG, '1', corner[0])
        agent.send_chat('放置lv 1猩猩')
        placed_gorilla.add((corner[0], '1'))
        del corner[0]

    #upgrade
    if agent.get_money(True) >= 1200 and 3 <= balance and len(placed_gorilla) != 0:
        temp = placed_gorilla.pop()
        if agent.get_money(True) >= 2800 and temp[1] != '3':
            agent.send_chat('放置lv 3猩猩')
            agent.place_tower(api.TowerType.DONKEY_KONG, '3b', temp[0])
            placed_gorilla.add((temp[0], '3'))
            balance -= 1
        elif temp[1] == '1':
            agent.send_chat('放置lv 2猩猩')
            agent.place_tower(api.TowerType.DONKEY_KONG, '2b', temp[0])
            placed_gorilla.add((temp[0], '2'))
            balance -= 1

    elif agent.get_money(True) >= 1200 and len(placed_bomb) != 0:
        temp = placed_bomb.pop()
        if agent.get_money(True) >= 2800 and temp[1] != '3':
            agent.send_chat('放置lv 3砲塔')
            agent.place_tower(api.TowerType.FORT, '3a', temp[0])
            placed_bomb.add((temp[0], '3'))
            balance += 1
        elif temp[1] == '1':
            agent.send_chat('放置lv 2砲塔')
            agent.place_tower(api.TowerType.FORT, '2a', temp[0])
            placed_bomb.add((temp[0], '2'))
            balance += 1


'''
while True:
    remain_time = agent.get_remain_time()
    agent.send_chat('test')
    # CAST DOUBLE INCOME
    income_multiplier: int = 1
    agent.cast_spell(api.SpellType.DOUBLE_INCOME)
    income_multiplier = 2

    # INCOME ENHANCEMENT
    if agent.get_income(True) / income_multiplier < 150:
        agent.spawn_unit(api.EnemyType.GOOMBA)
    elif len(agent.get_all_towers(True)) > 20 and agent.get_income(True) / income_multiplier < 250:
        agent.spawn_unit(api.EnemyType.GOOMBA)

    # DEFENSE
    terrain = agent.get_all_terrain()
    for (row, data) in enumerate(terrain):
        for (col, tile) in enumerate(data):
            if tile == api.TerrainType.EMPTY:
                agent.place_tower(api.TowerType.FIRE_MARIO, '1', api.Vector2(row, col))

    # ATTACK
    if agent.get_money(True) >= 3000:
        agent.spawn_unit(api.EnemyType.KOOPA_JR)

    # CHAT
'''
