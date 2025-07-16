# Copyright © 2025 mtmatt. All rights reserved.

import api
import time

agent = api.GameClient(7749, '6ad4da8e') #記得改token
#    左  上  右  下, 相對位置計算
dx = [-1, 0, 1, 0]
dy = [0, -1, 0, 1]
# 儲存好的放置地點
bomb_tower = [] #長條兩端
corner = [] #90度角

placed_bomb = set() #標註放置位置及等級
placed_gorilla = set() #標註放置位置及等級
balance = 0 #等等解釋
#讀取及儲存地形
terrain = agent.get_all_terrain()
rows = len(terrain)
cols = len(terrain[0])
#設定聊天欄
agent.set_chat_name_color("7fffd4")
agent.set_name("qhx338")
start = time.time()
#存長條、內角
for row in range(rows):#跑過每個座標
    for col in range(cols):
        if terrain[row][col] == api.TerrainType.EMPTY: #if 座標 = 可放置格

            for k in range(4):#找上下左右 有沒有道路
                count = 0
                temp_row = row
                temp_col = col
                is_corner = False
                next_row = temp_row + dx[k] #以下為找角落 (35 ~ 40)
                next_col = temp_col + dy[k]

                if terrain[next_row][next_col] == api.TerrainType.ROAD:
                    if terrain[row + dx[(k+1) % 4]][col + dy[(k+1) % 4]] == api.TerrainType.ROAD:
                        corner.append(api.Vector2(temp_row, temp_col))

                    else:
                        while (terrain[next_row][next_col] == api.TerrainType.ROAD): #以下為找長條道路兩端 (42~51)
                            next_row += dx[k]
                            next_col += dy[k]
                            if not (0 <= next_row < rows and 0 <= next_col < cols):
                                break
                            count += 1
                        if count >= 5:
                            if terrain[next_row][next_col] == api.TerrainType.OUT_OF_BOUNDS and terrain[next_row][next_col] == api.TerrainType.OBSTACLE:
                                bomb_tower.append(api.Vector2(next_row, next_col))
                            bomb_tower.append(api.Vector2(temp_row, temp_col))

#彩蛋別管
pixel_cat = agent.pixelcat()
agent.send_chat(pixel_cat)

while True: #主遊戲
    remain_time = agent.get_remain_time()
    end = time.time()#紀錄現在時間
    dt = end - start
    if(dt >= 3): #每3秒召喚一次 "票"寶寶
        agent.spawn_unit(api.EnemyType.GOOMBA)
        start = end

    if agent.get_spell_cooldown(True, api.SpellType.DOUBLE_INCOME) == 0: #兩倍錢
        agent.cast_spell(api.SpellType.DOUBLE_INCOME)
        agent.send_chat('兩倍錢>:)')

    """以下邏輯解釋:75~86
    當錢大於400 且有效位置還有剩 :
        放置砲塔
        將座標及等級存入 placed_bomb 裡 (升級時會用到)
    猩猩邏輯一樣
    """
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

    """以下邏輯解釋:75~86
    當錢大於1200 且有效位置還有剩 :
        如果錢大於2800:
            直接升級lv3b
        升級lv2
        將座標及等級存入 placed_gorilla 裡 (升級時會用到)
    砲台邏輯一樣
    """
    #balance值:每個砲臺升一級，balance值加一，大於三時則會開始升級猩猩
    if agent.get_money(True) >= 1200 and 3 >= balance and len(placed_gorilla) != 0:
        temp = placed_gorilla.pop()
        if agent.get_money(True) >= 2800:
            agent.send_chat('放置lv 3猩猩')
            agent.place_tower(api.TowerType.DONKEY_KONG, '3a', temp[0])
            balance -= 1
        elif temp[1] == '1':
            agent.send_chat('放置lv 2猩猩')
            agent.place_tower(api.TowerType.DONKEY_KONG, '2a', temp[0])
            placed_gorilla.add((temp[0], '2'))
            balance -= 1

    elif agent.get_money(True) >= 1200 and len(placed_bomb) != 0:
        temp = placed_bomb.pop()
        if agent.get_money(True) >= 2800:
            agent.send_chat('放置lv 3砲塔')
            agent.place_tower(api.TowerType.FORT, '3b', temp[0])
            balance += 1
        elif temp[1] == '1':
            agent.send_chat('放置lv 2砲塔')
            agent.place_tower(api.TowerType.FORT, '2b', temp[0])
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
