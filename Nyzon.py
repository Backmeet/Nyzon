import networking
import pygame as pg

pg.init()

width, height = 900, 600
screen = pg.display.set_mode((width, height))
title_font = pg.font.SysFont(None, 35)
description_font = pg.font.SysFont(None, 20)
NYZON_PORT = 51250
NETWORKPY_PORT = 51251

UserHere = networking.UserNode(input("UserName?:"))  # Replace "username" with the actual username
list_to_show = []
selected_group_index = 0
selected_item_index = 0

# Functions
def const(x, min_val, max_val):
    return min(max_val, max(min_val, x))

def draw_menu():
    global list_to_show
    if not list_to_show:
        list_to_show = UserHere.server_ask_getlist()
    if list_to_show:
        screen.fill((255, 255, 255))
        pg.draw.rect(screen, (0, 0, 0), (0, 0, width - 20, height - 20), 20)

        group_text = title_font.render(f"Group {selected_group_index}", True, (0, 0, 0))
        screen.blit(group_text, (50, 50))

        if len(list_to_show) > selected_group_index:
            group = list_to_show[selected_group_index]
            if isinstance(group, list):
                item_height = (height - 150) // 5  # Calculate height for each item box
                for i, item in enumerate(group):
                    if isinstance(item, dict) and 'name' in item and 'description' in item:
                        item_rect = pg.Rect(50, 100 + i * (item_height + 120), width - 120, item_height + 100)
                        pg.draw.rect(screen, (0, 0, 0), item_rect, 3)  # Draw border for each item
                        name_text = title_font.render(f"Title/Name: {item['name']}", True, (0, 0, 0))
                        description_text = description_font.render(f"Description: {item['description']}", True, (0, 0, 0))
                        instock_text = description_font.render(f"In stock: {item['instock']} How much: {item['howmanyinstock']}", True, (0, 0, 0))
                        price_text = description_font.render(f"Price: {item['price']}", True, (0, 0, 0))
                        screen.blit(name_text, (60, 110 + i * (item_height + 120)))
                        screen.blit(description_text, (60, 140 + i * (item_height + 120)))
                        screen.blit(instock_text, (60, 170 + i * (item_height + 120)))
                        screen.blit(price_text, (60, 200 + i * (item_height + 120)))

        pg.display.flip()
    else:
        print("Failed to get list from server")


# Main loop
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                if pg.key.get_mods() & pg.KMOD_SHIFT:
                    selected_group_index = const(selected_group_index + 1, 0, len(list_to_show) - 1)
                else:
                    selected_item_index = const(selected_item_index + 1, 0, 4)
            elif event.key == pg.K_DOWN:
                if pg.key.get_mods() & pg.KMOD_SHIFT:
                    selected_group_index = const(selected_group_index - 1, 0, len(list_to_show) - 1)
                else:
                    selected_item_index = const(selected_item_index - 1, 0, 4)

    list_to_show = UserHere.server_ask_getlist()

    draw_menu()

