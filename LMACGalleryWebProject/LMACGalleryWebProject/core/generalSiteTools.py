from LMACGalleryWebProject.settings import MAIN_MENU, TITLE_TEMPLATE


def mainMenuHelper(activeMenuItem: str):
    mainMenu = []
    for menuId in MAIN_MENU.keys():
        mainMenu.append(
            {
                'class': menuId + ' active' if menuId == activeMenuItem else menuId,
                'title': MAIN_MENU[menuId]['title'],
                'path': MAIN_MENU[menuId]['path'],
                'disabled': '' if MAIN_MENU[menuId]['enabled'] else ' disabled'
            }
        )
    return mainMenu


def pageTitleHelper(titleAddon: str) -> str:
    return TITLE_TEMPLATE.format(addon=titleAddon)

