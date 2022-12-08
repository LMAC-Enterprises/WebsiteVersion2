from LMACGalleryWebProject.settings import MAIN_MENU


def mainMenuHelper(activeMenuItem: str):
    mainMenu = []
    for menuId in MAIN_MENU.keys():
        mainMenu.append(
            {
                'class': menuId + ' active' if menuId == activeMenuItem else menuId,
                'title': MAIN_MENU[menuId]['title'],
                'path': MAIN_MENU[menuId]['path']
            }
        )
    return mainMenu


