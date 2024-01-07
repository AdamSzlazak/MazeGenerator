import customtkinter
import constants

class MainFrame:
    def __init__(self) -> None:
        self = customtkinter.CTk()
        self.geometry(f"{constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")

def createMainWindow() -> customtkinter:
    mainWindow = customtkinter.CTk()
    mainWindow.geometry(f"{constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
    mainWindow.title(constants.T.TITLE)
    return mainWindow

root = createMainWindow()

root.mainloop()