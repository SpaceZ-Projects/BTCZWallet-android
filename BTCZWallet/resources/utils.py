

from toga import App
from ..framework import Configuration, Point



class Utils:
    def __init__(self, app:App, activity):

        self.app = app
        self.activity = activity


    def screen_size(self):
        for screen in self.app.screens:
            width = screen.size.width
        return width

    def screen_resolution(self):
        configuration = self.activity.getResources().getConfiguration()
        window_manager = self.activity.getWindowManager()
        display = window_manager.getDefaultDisplay()
        size = Point()
        display.getRealSize(size)
        width = size.x
        height = size.y
        if configuration.orientation == Configuration.ORIENTATION_PORTRAIT:
            x = width
        else:
            x = height
        return x