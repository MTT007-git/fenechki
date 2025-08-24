from tkinter import *
import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from tkinter.ttk import Radiobutton, Notebook, Entry, Separator, Button, Style, Combobox
from PIL import Image, ImageTk
import PIL.ImageFile
import math
import os
import typing

# Constants
DIAMOND_WIDTH: int = 20
DIAMOND_HEIGHT: int = 30
SMALL_CIRCLE_RADIUS: int = 12
BIG_CIRCLE_RADIUS: int = 150
ICON_HEIGHT: int = 24
TAB_ICON_HEIGHT: int = 12
BUTTON_ICON_HEIGHT: int = 15
SHADOW_OFFSET: int = 10

# Files
directory: str = "Custom"
button_image_path: str = f"{directory}/button.png"
l_click_path: str = f"{directory}/l_click.png"
r_click_path: str = f"{directory}/r_click.png"
edit_path: str = f"{directory}/edit.png"
plus_path: str = f"{directory}/plus.png"
delete_path: str = f"{directory}/delete.png"
filenames_path: str = f"{directory}/filenames.txt"


_all_icons: dict[tuple[str, bool], ImageTk.PhotoImage] = {}  # otherwise icons from geticon() get garbage-collected


def geticon(icon_path: str, is_tab: bool = False, height: int | None = None) -> ImageTk.PhotoImage:
    """
    Makes a PhotoImage to use as an icon
    :param icon_path: path to icon
    :param is_tab: smaller icon size to use as a Notebook tab image
    :param height: icon height (overrides is_tab)
    :return: PhotoImage to use as an icon
    """
    if _all_icons.get((icon_path, is_tab), None) is not None:
        return _all_icons[(icon_path, is_tab)]

    if height is None:
        if is_tab:
            height: int = TAB_ICON_HEIGHT
        else:
            height: int = ICON_HEIGHT

    icon: PIL.ImageFile.ImageFile = Image.open(icon_path)
    icon_ratio: float = icon.width / icon.height
    icon: Image.Image = icon.resize((int(height * icon_ratio), height), Image.Resampling.LANCZOS)
    icon: ImageTk.PhotoImage = ImageTk.PhotoImage(icon)
    _all_icons[(icon_path, is_tab)] = icon  # prevent garbage collection
    return icon


# Custom widgets

class Colorbutton(tk.Button):
    """
    Button widget with a colorpicker
    """
    def __init__(self, master: Misc | None = None, color: str | tuple[int, int, int] = "#ffffff", *args, **kwargs
                 ) -> None:
        """
        Construct a button widget with a colorpicker with the parent MASTER.
        :param master: parent
        :param color: starting color
        :param args: Button options
        :param kwargs: Button options
        """
        self._button_img: PIL.ImageFile.ImageFile = Image.open(button_image_path).convert("RGBA")

        self.color: str | tuple[int, int, int] = color
        buttonimg: ImageTk.PhotoImage = self._create_button_img(self.color)
        super().__init__(master, image=buttonimg, border=0, relief="sunken", *args, **kwargs)
        self.image: ImageTk.PhotoImage = buttonimg

    def set_color(self, color: str | tuple[int, int, int]) -> None:
        """
        Sets the button's color
        :param color: new button color
        :return: None
        """
        self.color = color
        main_img: ImageTk.PhotoImage = self._create_button_img(self.color)
        self.configure(image=main_img)
        self.image = main_img

    def _create_button_img(self, color: str | tuple[int, int, int]) -> ImageTk.PhotoImage:
        """
        Function that generates a button image with a color
        Not intended for use ouside widget's class
        :param color: color of the button image
        :return: button image
        """
        img: Image.Image = self._button_img.copy()
        color_overlay: Image.Image = Image.new("RGBA", img.size, color)
        img = Image.alpha_composite(color_overlay, img)
        return ImageTk.PhotoImage(img)


class Labelentry(LabelFrame):
    """
    Entry widget in a LabelFrame
    """
    def __init__(self, master: Misc | None = None, text: str = "", *args, **kwargs) -> None:
        """
        Construct an Entry widget inside a LabelFrame with the parent MASTER.
        :param master: parent
        :param text: LabelFrame text
        :param args: Entry options
        :param kwargs: Entry options
        """
        super().__init__(master, text=text)

        self.entry: Entry = Entry(self, *args, **kwargs)
        self.entry.pack()

        self.messagelabel: Label | None = None

    def showmessage(self, text: str, *args, **kwargs) -> None:
        """
        Show a Label under the Entry to the user
        :param text: Label text
        :param args: Label options
        :param kwargs: Label options
        :return: None
        """
        if self.messagelabel:
            self.messagelabel.destroy()
            self.messagelabel = None
        self.messagelabel = Label(self, text=text, *args, **kwargs)
        self.messagelabel.pack()

    def delmessage(self) -> None:
        """
        Deletes the Label shown by showmassage, if any
        :return: None
        """
        if self.messagelabel:
            self.messagelabel.destroy()
            self.messagelabel = None


class Labelcombobox(LabelFrame):
    """
    Combobox widget inside a LabelFrame
    """
    def __init__(self, master: Misc | None = None, text: str = "", values: list[str] | None = None,
                 *args, **kwargs) -> None:
        """
        Construct a Combobox widget inside a LabelFrame with the parent MASTER.
        :param master: parent
        :param text: LabelFrame text
        :param values: Combobox values
        :param args: Combobox options
        :param kwargs: Combobox options
        """
        super().__init__(master, text=text)

        if values is None:
            values = ["Choose"]
        self.combobox: Combobox = Combobox(self, state="readonly", values=values, *args, **kwargs)
        self.combobox.pack()

        self.messagelabel: Label | None = None

    def showmessage(self, text: str, *args, **kwargs) -> None:
        """
        Show a Label under the Entry to the user
        :param text: Label text
        :param args: Label options
        :param kwargs: Label options
        :return: None
        """
        if self.messagelabel:
            self.messagelabel.destroy()
            self.messagelabel = None
        self.messagelabel = Label(self, text=text, *args, **kwargs)
        self.messagelabel.pack()

    def delmessage(self) -> None:
        """
        Deletes the Label shown by showmassage, if any
        :return: None
        """
        if self.messagelabel:
            self.messagelabel.destroy()
            self.messagelabel = None


class Labelfilechooser(Labelentry):
    """
    Entry and Button widgets inside a LabelFrame, connected to form a filechooser
    """
    def __init__(self, master: Misc | None = None, text: str = "", filedialogcmd: typing.Callable | None = None,
                 textvariable: Variable = None, command: typing.Callable | None = None, *args, **kwargs) -> None:
        """
        Construct a filechooser inside a LabelFrame with the parent MASTER.
        :param master: parent
        :param text: LabelFrame text
        :param filedialogcmd: command to show a filedialog (example: askopenfilename)
        :param textvariable: Entry textvariable
        :param command: command to execute when an existing filename is in the Entry
        :param args: Entry options
        :param kwargs: Entry options
        """
        if textvariable is None:
            textvariable = StringVar()
        super().__init__(master, text, textvariable=textvariable, *args, **kwargs)

        if not filedialogcmd:
            filedialogcmd = filedialog.askopenfilename

        self.command: typing.Callable = command
        self.textvariable: Variable = textvariable
        self.textvariable.trace_add("write", lambda a, b, c: self.validate())

        self.buttonframe: Frame = Frame(self)
        self.buttonframe.pack(side="bottom")
        Button(self.buttonframe, text="Browse...", command=lambda: self.browse(filedialogcmd)).grid(row=0, column=0)

    def browse(self, cmd: typing.Callable) -> None:
        """
        Choose file to put in the Entry
        :param cmd: command to show a filedialog (example: askopenfilename)
        :return: None
        """
        res: typing.Any = cmd()
        if res:
            self.textvariable.set(res)

    def validate(self) -> None:
        """
        Gets called when the Entry is changed, calls command from __init__ when an existing filename is in the Entry
        :return: None
        """
        if not os.path.exists(self.textvariable.get()) and self.textvariable.get() != "":
            self.showmessage("Path doesn't exist", fg="red")
        elif self.textvariable.get().find(".") == -1 and self.textvariable.get() != "":
            self.showmessage("Not a file", fg="red")
        else:
            self.delmessage()
            if self.command:
                self.command()


# Works, but will be removed after Custom class is complete. Will not be documented.
class Kumihimo(Frame):
    """
    Not documented
    """
    def __init__(self, master, toplevel, name="Kumihimo", icon=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.toplevel = toplevel
        self.name = name

        self.icon = icon
        if icon is not None:
            self.icon = geticon(self.icon, True)

        self.circle_radius = BIG_CIRCLE_RADIUS
        self.rows = 7
        self.cols = 5
        self.canvas_width = self.canvas_height = 0
        self.calc_size()

        self.color = "#ff0000"
        self.alt_color = "#ffffff"

        color_frame = Frame(self)
        color_frame.grid(row=0, column=0, sticky="nw")

        self.colorbtn = Colorbutton(color_frame, self.color, command=self.choose_color)

        self.alt_colorbtn = Colorbutton(color_frame, self.alt_color, command=self.choose_alt_color)

        left_label = Label(color_frame, image=geticon(l_click_path))
        right_label = Label(color_frame, image=geticon(r_click_path))

        self.colorbtn.grid(column=0, row=0, sticky="w")
        left_label.grid(column=1, row=0, sticky="w")

        self.alt_colorbtn.grid(column=0, row=1, sticky="w")
        right_label.grid(column=1, row=1, sticky="w")

        self.thread_mode = IntVar(value=16)
        self.threads = self.thread_mode.get()
        thread_frame = Frame(self)
        thread_frame.grid(row=0, column=1, sticky="w", padx=10)
        Radiobutton(thread_frame, text="16 threads", variable=self.thread_mode, value=16,
                    command=self.update_circle).pack(anchor="w")
        Radiobutton(thread_frame, text="8 threads", variable=self.thread_mode, value=8,
                    command=self.update_circle).pack(anchor="w")

        self.canvas = Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.grid(column=0, row=2, columnspan=2)

        self.diamond_ids = {}  # item_id: (points, cx, cy)
        self.circle_ids = {}
        self.circle_colors = {}
        self.logical_coords = {}  # item_id: (x, y) in logical grid coords
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click_left)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<Button-3>", self.on_click_right)
        self.canvas.bind("<MouseWheel>", lambda event: self.on_scroll(int(event.delta > 0) * 2 - 1))  # Windows
        self.canvas.bind("<Button-4>", lambda event: self.on_scroll(1))  # Linux MouseWheel-Up
        self.canvas.bind("<Button-5>", lambda event: self.on_scroll(-1))  # Linux MouseWheel-Down

    def calc_size(self):
        self.canvas_width = ((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH +
                             self.circle_radius * 2 + 40 + SHADOW_OFFSET * 2)
        self.canvas_height = (2 * (self.rows - 1) - 1) * DIAMOND_HEIGHT + 2 * DIAMOND_HEIGHT + SHADOW_OFFSET * 2

        try:
            self.toplevel.set_geometry()
        except AttributeError:
            pass

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.color, title="Choose Primary Color")
        if color[1]:
            self.set_color(0, color[1])

    def choose_alt_color(self):
        color = colorchooser.askcolor(initialcolor=self.alt_color, title="Choose Secondary Color")
        if color[1]:
            self.set_color(1, color[1])

    def set_color(self, is_alt, fill_color):
        if is_alt:
            self.alt_color = fill_color
            self.alt_colorbtn.set_color(self.alt_color)
        else:
            self.color = fill_color
            self.colorbtn.set_color(self.color)

    def draw_diamond(self, cx, cy, w, h, logical_coords, delpoints=()):
        points = [cx, cy - h, cx + w, cy, cx, cy + h, cx - w, cy]
        for i in sorted(delpoints, reverse=True):
            points.pop(i * 2)
            points.pop(i * 2)
        if len(points) <= 4:
            points.append(cx)
            points.append(cy)
        item = self.canvas.create_polygon(points, fill="white", outline="black")
        self.diamond_ids[item] = (points, cx, cy)
        self.logical_coords[item] = logical_coords

    def draw_grid(self):
        offset_x, offset_y = 5, 5

        delpoints = []
        for row in range(self.rows):
            for col in range(self.cols):
                if row == 0:
                    delpoints.append(0)
                if col == 0:
                    delpoints.append(3)
                if col == self.cols - 1:
                    delpoints.append(1)
                cx = offset_x + col * 2 * DIAMOND_WIDTH
                cy = offset_y + row * 2 * DIAMOND_HEIGHT
                self.draw_diamond(cx, cy, DIAMOND_WIDTH, DIAMOND_HEIGHT, (col, row), delpoints)
                delpoints = []

        for row in range(self.rows):
            for col in range(self.cols - 1):
                if row == self.rows - 1:
                    delpoints.append(2)
                cx = offset_x + col * 2 * DIAMOND_WIDTH + DIAMOND_WIDTH
                cy = offset_y + row * 2 * DIAMOND_HEIGHT + DIAMOND_HEIGHT
                self.draw_diamond(cx, cy, DIAMOND_WIDTH, DIAMOND_HEIGHT, (col + 0.5, row + 0.5), delpoints)
                delpoints = []

        self.draw_circle_of_circles()

    def draw_circle_of_circles(self):
        for item in list(self.circle_ids):
            if self.canvas.gettags(item) == ("circle",):
                self.canvas.delete(item)
                self.circle_ids.pop(item)

        cx = (2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH + self.circle_radius + 20 + SHADOW_OFFSET
        cy = ((2 * (self.rows - 1) - 1) * DIAMOND_HEIGHT + 2 * DIAMOND_HEIGHT) // 2 + SHADOW_OFFSET

        shadow_radius = self.circle_radius + SMALL_CIRCLE_RADIUS + SHADOW_OFFSET
        self.canvas.create_oval(
            cx - shadow_radius, cy - shadow_radius,
            cx + shadow_radius, cy + shadow_radius,
            fill="#eee", outline="", tags="circle"
        )

        mod = 32 / self.threads * 2
        for i in range(32):
            if i % mod >= 2:
                continue
            angle = 2 * math.pi * (i - 0.5) / 32
            x = cx + self.circle_radius * math.sin(angle)
            y = cy - self.circle_radius * math.cos(angle)
            item = self.canvas.create_oval(
                x - SMALL_CIRCLE_RADIUS, y - SMALL_CIRCLE_RADIUS,
                x + SMALL_CIRCLE_RADIUS, y + SMALL_CIRCLE_RADIUS,
                fill=self.circle_colors.get(i, "white"), outline="black", tags="circle"
            )
            self.circle_ids[item] = (x, y, i)
            self.circle_colors[i] = self.circle_colors.get(i, "white")

    def update_circle(self):
        if self.threads != self.thread_mode.get():
            self.threads = self.thread_mode.get()

            # Reset all diamond fills to white
            for item_id in self.diamond_ids:
                self.canvas.itemconfig(item_id, fill="white")

            # Reset circle colors
            self.circle_colors = {}

        # Redraw
        self.draw_circle_of_circles()

    def redraw_diamonds(self):
        mod = 32 / self.threads * 2
        for i in range(32):
            if i % mod >= 2:
                continue
            self.fill_circle(i, self.circle_colors.get(i, "white"))

    def point_inside_polygon(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0], poly[1]
        xinters = 0
        for i in range(2, n + 2, 2):
            p2x, p2y = poly[i % n], poly[(i + 1) % n]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def set_diamond(self, x, y, color):
        if 0 <= x < self.cols - 0.5 and 0 <= y <= self.rows:
            self.canvas.itemconfig(
                list(self.logical_coords.keys())[list(self.logical_coords.values()).index((x, y))], fill=color)
            return True
        return False

    def set_circle(self, n, color):
        self.canvas.itemconfig([i for i, j in self.circle_ids.items() if j[2] == n][0], fill=color)
        self.circle_colors[n] = color

    def fill_circle(self, circle, color=None):
        if color:
            self.set_circle(circle, color)
        start_x = 3 - math.floor(circle % 16 / (32 / self.threads * 2))
        shift = math.floor(circle / 16) * 2 + circle % 2
        start_x = start_x - 0.5 * shift
        start_y = 0.5 * shift
        shift = (-0.5 * 4, 0.5 * 4)
        sh = math.log(self.threads // 4, 2) % 2 * 2 + 1
        start_shift = (0.5 * (self.threads // 4) - (0.5 * sh), 0.5 * (self.threads // 4) + (0.5 * sh))
        if self.threads // 4 < 4:
            start_x -= start_shift[0]
            start_y -= start_shift[1]
        diamonds = set()
        while start_y < self.rows:
            x = start_x
            y = start_y
            while 0 <= x and y < self.rows:
                diamonds.add((x, y))
                if color:
                    self.set_diamond(x, y, color)
                x += shift[0]
                y += shift[1]
            start_x += start_shift[0]
            start_y += start_shift[1]
            x = start_x
            y = start_y
            while x < self.rows - 0.5 and 0 <= y:
                start_x, start_y = x, y
                x += 0.5 * 4
                y -= 0.5 * 4
        return diamonds

    def get_circle(self, logical_x, logical_y):
        mod = 32 / self.threads * 2
        for i in range(32):
            if i % mod >= 2:
                continue
            if (logical_x, logical_y) in self.fill_circle(i):
                return i
        raise RuntimeWarning(f"Nothing found: {logical_x}, {logical_y}")

    def handle_click(self, event, color):
        clicked = self.canvas.find_closest(event.x, event.y)
        if clicked:
            item_id = clicked[0]
            if item_id in self.logical_coords:
                points, _, _ = self.diamond_ids[item_id]
                if not self.point_inside_polygon(event.x, event.y, points):
                    return
                self.fill_circle(self.get_circle(*self.logical_coords[item_id]), color)
            elif item_id in self.circle_ids:
                cx, cy, n = self.circle_ids[item_id]
                dist = math.hypot(event.x - cx, event.y - cy)
                if dist <= SMALL_CIRCLE_RADIUS:
                    self.fill_circle(n, color)

    def on_click_left(self, event):
        self.handle_click(event, self.color)

    def on_click_right(self, event):
        self.handle_click(event, self.alt_color)

    def on_middle_click(self, event):
        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return

        item_id = clicked[0]

        # Check for Shift key — 0x0001 or 0x0004 are commonly used across platforms
        pick_alt = (event.state & 0x0001) != 0 or (event.state & 0x0004) != 0

        if item_id in self.diamond_ids:
            points, _, _ = self.diamond_ids[item_id]
            if self.point_inside_polygon(event.x, event.y, points):
                fill_color = self.canvas.itemcget(item_id, "fill")
                if fill_color:
                    self.set_color(pick_alt, fill_color)

        elif item_id in self.circle_ids:
            cx, cy, _ = self.circle_ids[item_id]
            dist = math.hypot(event.x - cx, event.y - cy)
            if dist <= SMALL_CIRCLE_RADIUS:
                fill_color = self.canvas.itemcget(item_id, "fill")
                if fill_color:
                    self.set_color(pick_alt, fill_color)

    def on_scroll(self, scroll):
        pass
        # new_circle_colors = self.circle_colors.copy()
        # for i, j in self.circle_colors.items():
        #     new_circle_colors[(i + scroll * (32 / self.threads * 2)) % 32] = j
        # self.circle_colors = new_circle_colors
        # self.update_circle()
        # self.redraw_diamonds()


# Does not work properly, will be removed after Custom class is complete. Will not be documented.
class Flat(Frame):
    """
    Not documented
    """
    def __init__(self, master, toplevel, name="Flat", icon=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.toplevel = toplevel
        self.name = name

        self.icon = icon
        if icon is not None:
            self.icon = geticon(self.icon, True)

        self.rows = 7
        self.cols = 4
        self.canvas_width = self.canvas_height = 0
        self.threads = 13
        self.calc_size()

        self.color = "#ff0000"
        self.alt_color = "#ffffff"

        color_frame = Frame(self)
        color_frame.grid(row=0, column=0, sticky="nw")

        self.colorbtn = Colorbutton(color_frame, self.color, command=self.choose_color)

        self.alt_colorbtn = Colorbutton(color_frame, self.alt_color, command=self.choose_alt_color)

        left_label = Label(color_frame, image=geticon(l_click_path))
        right_label = Label(color_frame, image=geticon(r_click_path))

        self.colorbtn.grid(column=0, row=0, sticky="w")
        left_label.grid(column=1, row=0, sticky="w")

        self.alt_colorbtn.grid(column=0, row=1, sticky="w")
        right_label.grid(column=1, row=1, sticky="w")

        self.thread_mode = IntVar(value=13)
        self.thread_mode.trace_add("write", lambda a, b, c: self.update_circles())
        self.threads = self.thread_mode.get()
        thread_frame = Frame(self)
        thread_frame.grid(row=0, column=1, sticky="w", padx=10)

        self.thread_entry = Entry(thread_frame, textvariable=self.thread_mode,
                                  validatecommand=(master.register(lambda s: s.isdigit() or s == ""), "%P"),
                                  validate="key")
        self.thread_entry.pack(anchor="w")
        self.thread_info = Label(thread_frame, text="")
        self.thread_info.pack(anchor="w")

        self.canvas = Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.grid(column=0, row=2, columnspan=2, sticky="w")
        self.calc_size()

        self.diamond_ids = {}  # item_id: (points, cx, cy)
        self.circle_ids = {}
        self.circle_colors = {}
        self.logical_coords = {}  # item_id: (x, y) in logical grid coords
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click_left)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<Button-3>", self.on_click_right)
        self.canvas.bind("<MouseWheel>", lambda event: self.on_scroll(int(event.delta > 0) * 2 - 1))  # Windows
        self.canvas.bind("<Button-4>", lambda event: self.on_scroll(1))  # Linux MouseWheel-Up
        self.canvas.bind("<Button-5>", lambda event: self.on_scroll(-1))  # Linux MouseWheel-Down

    def calc_size(self):
        self.canvas_width = ((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH +
                             SMALL_CIRCLE_RADIUS * (self.threads + 1) * 2 + 40 + SHADOW_OFFSET * 2)
        self.canvas_height = (2 * (self.rows - 1) - 1) * DIAMOND_HEIGHT + 2 * DIAMOND_HEIGHT + SHADOW_OFFSET * 2

        try:
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            self.toplevel.set_geometry()
        except AttributeError:
            pass

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.color, title="Choose Primary Color")
        if color[1]:
            self.set_color(0, color[1])

    def choose_alt_color(self):
        color = colorchooser.askcolor(initialcolor=self.alt_color, title="Choose Secondary Color")
        if color[1]:
            self.set_color(1, color[1])

    def set_color(self, is_alt, fill_color):
        if is_alt:
            self.alt_color = fill_color
            self.alt_colorbtn.set_color(self.alt_color)
        else:
            self.color = fill_color
            self.colorbtn.set_color(self.color)

    def draw_diamond(self, cx, cy, w, h, logical_coords, delpoints=()):
        points = [cx, cy - h, cx + w, cy, cx, cy + h, cx - w, cy]
        for i in sorted(delpoints, reverse=True):
            points.pop(i * 2)
            points.pop(i * 2)
        if len(points) <= 4:
            points.append(cx)
            points.append(cy)
        item = self.canvas.create_polygon(points, fill="white", outline="black", tags="diamond")
        self.diamond_ids[item] = (points, cx, cy)
        self.logical_coords[item] = logical_coords

    def draw_grid(self):
        for item in list(self.diamond_ids.keys()):
            if self.canvas.gettags(item) == ("diamond",):
                self.canvas.delete(item)
                self.diamond_ids.pop(item)

        offset_x, offset_y = 5, 5

        delpoints = []
        for row in range(self.rows):
            for col in range(self.cols):
                if row == 0:
                    delpoints.append(0)
                if col == 0:
                    delpoints.append(3)
                if col == self.cols - 1:
                    delpoints.append(1)
                cx = offset_x + col * 2 * DIAMOND_WIDTH
                cy = offset_y + row * 2 * DIAMOND_HEIGHT
                self.draw_diamond(cx, cy, DIAMOND_WIDTH, DIAMOND_HEIGHT, (col, row), delpoints)
                delpoints = []

        for row in range(self.rows):
            for col in range(self.cols - 1):
                if row == self.rows - 1:
                    delpoints.append(2)
                cx = offset_x + col * 2 * DIAMOND_WIDTH + DIAMOND_WIDTH
                cy = offset_y + row * 2 * DIAMOND_HEIGHT + DIAMOND_HEIGHT
                self.draw_diamond(cx, cy, DIAMOND_WIDTH, DIAMOND_HEIGHT, (col + 0.5, row + 0.5), delpoints)
                delpoints = []

        self.draw_circles()

    def draw_circles(self):
        for item in list(self.circle_ids):
            if self.canvas.gettags(item) == ("circle",):
                self.canvas.delete(item)
                self.circle_ids.pop(item)

        cx = (((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH + 20 + SHADOW_OFFSET) +
              (self.canvas_width - ((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH + 20 +
                                    SHADOW_OFFSET * 7.5)) // 2)
        cy = ((2 * (self.rows - 1) - 1) * DIAMOND_HEIGHT + 2 * DIAMOND_HEIGHT) // 2

        sub = 0

        for i in range(self.threads + 1):
            if i == self.threads // 2:
                sub = 1
                continue
            x = cx + (i - self.threads / 2) * SMALL_CIRCLE_RADIUS * 2 + SMALL_CIRCLE_RADIUS
            y = cy
            item = self.canvas.create_oval(
                x - SMALL_CIRCLE_RADIUS, y - SMALL_CIRCLE_RADIUS,
                x + SMALL_CIRCLE_RADIUS, y + SMALL_CIRCLE_RADIUS,
                fill=self.circle_colors.get(i - sub, "white"), outline="black", tags="circle"
            )
            self.circle_ids[item] = (x, y, i - sub)
            self.circle_colors[i - sub] = self.circle_colors.get(i - sub, "white")

    def update_circles(self):
        if self.thread_entry.get() == "":
            self.thread_info.config(text="Not defined", fg="red")
            return
        elif self.thread_mode.get() > 35:
            self.thread_info.config(text="Too big", fg="red")
            return
        elif self.thread_mode.get() % 2 == 0:
            self.thread_info.config(text="Even threads", fg="red")
            return
        else:
            self.thread_info.config(text="", fg="black")
        if self.threads != self.thread_mode.get():
            self.threads = self.thread_mode.get()
            self.circle_colors = {}
            self.cols = self.threads // 4 + 1
            self.calc_size()

        self.draw_grid()

    def redraw_diamonds(self):
        mod = 32 / self.threads * 2
        for i in range(32):
            if i % mod >= 2:
                continue
            self.fill_circle(i, self.circle_colors.get(i, "white"))

    def point_inside_polygon(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0], poly[1]
        xinters = 0
        for i in range(2, n + 2, 2):
            p2x, p2y = poly[i % n], poly[(i + 1) % n]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def set_diamond(self, x, y, color):
        if 0 <= x < self.cols - 0.5 and 0 <= y <= self.rows:
            self.canvas.itemconfig(
                list(self.logical_coords.keys())[list(self.logical_coords.values()).index((x, y))], fill=color)
            return True
        return False

    def set_circle(self, n, color):
        self.canvas.itemconfig([i for i, j in self.circle_ids.items() if j[2] == n][0], fill=color)
        self.circle_colors[n] = color

    def fill_circle(self, circle, color=None):
        if color:
            self.set_circle(circle, color)
        # logic
        diamonds = []
        return diamonds

    def get_circle(self, logical_x, logical_y):
        mod = 32 / self.threads * 2
        for i in range(32):
            if i % mod >= 2:
                continue
            if (logical_x, logical_y) in self.fill_circle(i):
                return i
        raise RuntimeWarning(f"Nothing found: {logical_x}, {logical_y}")

    def handle_click(self, event, color):
        clicked = self.canvas.find_closest(event.x, event.y)
        if clicked:
            item_id = clicked[0]
            if item_id in self.logical_coords:
                points, _, _ = self.diamond_ids[item_id]
                if not self.point_inside_polygon(event.x, event.y, points):
                    return
                self.fill_circle(self.get_circle(*self.logical_coords[item_id]), color)
            elif item_id in self.circle_ids:
                cx, cy, n = self.circle_ids[item_id]
                dist = math.hypot(event.x - cx, event.y - cy)
                if dist <= SMALL_CIRCLE_RADIUS:
                    self.fill_circle(n, color)

    def on_click_left(self, event):
        self.handle_click(event, self.color)

    def on_click_right(self, event):
        self.handle_click(event, self.alt_color)

    def on_middle_click(self, event):
        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return

        item_id = clicked[0]

        # Check for Shift key — 0x0001 or 0x0004 are commonly used across platforms
        pick_alt = (event.state & 0x0001) != 0 or (event.state & 0x0004) != 0

        if item_id in self.diamond_ids:
            points, _, _ = self.diamond_ids[item_id]
            if self.point_inside_polygon(event.x, event.y, points):
                fill_color = self.canvas.itemcget(item_id, "fill")
                if fill_color:
                    self.set_color(pick_alt, fill_color)

        elif item_id in self.circle_ids:
            cx, cy, _ = self.circle_ids[item_id]
            dist = math.hypot(event.x - cx, event.y - cy)
            if dist <= SMALL_CIRCLE_RADIUS:
                fill_color = self.canvas.itemcget(item_id, "fill")
                if fill_color:
                    self.set_color(pick_alt, fill_color)

    def on_scroll(self, scroll):
        pass
        # new_circle_colors = self.circle_colors.copy()
        # for i, j in self.circle_colors.items():
        #     new_circle_colors[(i + scroll * (32 / self.threads * 2)) % 32] = j
        # self.circle_colors = new_circle_colors
        # self.update_circle()
        # self.redraw_diamonds()


# Editor for Custom class
class Editor(Frame):
    """
    Editor for Custom class
    """
    def __init__(self, master: Misc, *args, **kwargs) -> None:
        """
        Initialise the editor
        :param master: parent
        :param args: Frame options
        :param kwargs: Frame options
        """
        super().__init__(master, *args, **kwargs)

        self.is_open: bool = False

        Separator(self, orient="vertical").grid(row=0, column=0, rowspan=4, sticky="nsw")
        Label(self, text="Editor").grid(row=0, column=1, columnspan=2)
        self.namevar: StringVar = StringVar(value=self.master.name)
        self.namevar.trace_add("write", lambda a, b, c: self.master.updatetab(name=self.namevar.get()))
        Labelentry(self, text="Name", textvariable=self.namevar).grid(row=1, column=1, sticky="n")
        self.iconpathvar: StringVar = StringVar()
        iconchooser = Labelfilechooser(self, text="Icon", textvariable=self.iconpathvar,
                                       command=lambda: self.master.updatetab(icon=self.iconpathvar.get()),
                                       filedialogcmd=lambda: filedialog.askopenfilename(title="Choose icon", filetypes=[
                                           ("All images", ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.ico")),
                                           ("PNG", "*.png"),
                                           ("JPEG", ("*.jpg", "*.jpeg")), ("BMP", "*.bmp"), ("GIF", "*.gif"),
                                           ("ICO", "*.ico")],
                                                                                        initialdir=os.path.dirname(
                                                                                            self.iconpathvar.get()))
                                       )
        iconchooser.grid(row=1, column=2, sticky="n")
        Button(iconchooser.buttonframe, image=geticon(delete_path, height=BUTTON_ICON_HEIGHT), style="Red.TButton",
               command=lambda: self.iconpathvar.set("")).grid(row=0, column=1, sticky="w")
        self.compoundvar: StringVar = StringVar(value=self.master.compound)
        self.compoundvar.trace_add("write", lambda a, b, c: self.master.updatetab(compound=self.compoundvar.get()))
        Labelcombobox(iconchooser.buttonframe, text="Compound", values=["left", "right", "top", "bottom", "none"],
                      textvariable=self.compoundvar).grid(row=1, column=0, columnspan=2)
        Button(self, text="Delete", image=geticon(delete_path, True), compound="left",
               style="Red.TButton", command=self.master.delete).grid(row=3, column=2, sticky="es")

    def load(self, path: str) -> None:
        """
        Load configuration from file
        TODO: make loading/saving after the Editor is complete
        :param path: file path
        :return: None
        """
        pass


# Main class for designing a custom pattern
class Custom(Frame):
    """
    Main class for designing a custom pattern
    """
    def __init__(self, master: Misc, toplevel: Misc, path: str = None, name: str = "Custom", icon: str | None = None,
                 compound: str = "left", *args, **kwargs) -> None:
        """
        Constructs the class
        :param master: parent
        :param toplevel: toplevel window, usually Window
        :param path: path to saved file
        :param name: pattern name
        :param icon: path to icon
        :param compound: icon compound
        :param args: Frame options
        :param kwargs: Frame options
        """
        super().__init__(master, *args, **kwargs)

        self.toplevel: Misc = toplevel
        self.name: str = name
        self.compound: str = compound

        self.icon: str | None = icon
        if icon is not None:
            self.icon: ImageTk.PhotoImage = geticon(self.icon, True)

        self.editor: Editor = Editor(self)

        self.rows: int = 7
        self.cols: int = 4
        self.canvas_width: int = 0
        self.canvas_height: int = 0
        self.threads: int = 13
        self.calc_size(False)

        self.color: str | tuple[int, int, int] = "#ff0000"
        self.alt_color: str | tuple[int, int, int] = "#ffffff"

        color_frame: Frame = Frame(self)
        color_frame.grid(row=0, column=0, sticky="nw")

        self.colorbtn: Colorbutton = Colorbutton(color_frame, self.color, command=self.choose_color)

        self.alt_colorbtn: Colorbutton = Colorbutton(color_frame, self.alt_color, command=self.choose_alt_color)

        Label(color_frame, image=geticon(l_click_path)).grid(column=1, row=0, sticky="w")
        Label(color_frame, image=geticon(r_click_path)).grid(column=1, row=1, sticky="w")

        self.colorbtn.grid(column=0, row=0, sticky="w")
        self.alt_colorbtn.grid(column=0, row=1, sticky="w")

        self.thread_mode: IntVar = IntVar(value=13)
        self.thread_mode.trace_add("write", lambda a, b, c: self.update_circles())
        self.threads: int = self.thread_mode.get()
        thread_frame: Frame = Frame(self)
        thread_frame.grid(row=0, column=1, sticky="w", padx=10)

        self.thread_entry: Labelentry = Labelentry(thread_frame, text="Threads", textvariable=self.thread_mode,
                                                   validatecommand=(master.register(lambda s: s.isdigit() or s == ""),
                                                                    "%P"), validate="key")
        self.thread_entry.pack(anchor="w")

        Button(self, image=geticon(edit_path),
               command=lambda: self.close_editor() if self.editor.is_open else self.open_editor()).grid(row=0,
                                                                                                        column=2,
                                                                                                        sticky="ne")

        self.canvas: Canvas = Canvas(self, width=self.canvas_width, height=self.canvas_height,
                                     bg="SystemButtonFace", highlightthickness=0)
        self.canvas.grid(column=0, row=2, columnspan=2, sticky="w")
        self.calc_size()

        self.diamond_ids: dict[int, tuple[list[int], int, int]] = {}  # item_id: (points, cx, cy)
        self.circle_ids: dict[int, tuple[int, int, int]] = {}  # item_id: (x, y, i)
        self.circle_colors: dict[int, str | tuple[int, int, int]] = {}  # i: color
        self.logical_coords: dict[int, tuple[int, int]] = {}  # item_id: (x, y) in logical grid coords
        self.draw_grid()
        if path:
            self.editor.load(path)
        self.canvas.bind("<Button-1>", self.on_click_left)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<Button-3>", self.on_click_right)
        self.canvas.bind("<MouseWheel>", lambda event: self.on_scroll(int(event.delta > 0) * 2 - 1))  # Windows
        self.canvas.bind("<Button-4>", lambda event: self.on_scroll(1))  # Linux MouseWheel-Up
        self.canvas.bind("<Button-5>", lambda event: self.on_scroll(-1))  # Linux MouseWheel-Down

    def open_editor(self) -> None:
        """
        Open the editor
        :return: None
        """
        if not self.editor.is_open:
            self.editor.grid(row=0, column=3, rowspan=3, sticky="nesw")
        self.editor.is_open = True
        self.toplevel.set_geometry()

    def close_editor(self) -> None:
        """
        Close the editor
        :return: None
        """
        if self.editor.is_open:
            self.editor.grid_forget()
        self.editor.is_open = False
        self.toplevel.set_geometry()

    def updatetab(self, name: str = None, icon: ImageTk.PhotoImage | PhotoImage = None, compound: str = None) -> None:
        """
        Update this tab
        :param name: new name
        :param icon: new icon
        :param compound: new compound
        :return: None
        """
        if name is not None:
            self.name = name
        if icon is not None:
            if icon == "":
                self.icon = None
            else:
                self.icon = geticon(icon, True)
        if compound is not None:
            self.compound = compound
        self.toplevel.updatetab(self)

    def calc_size(self, update_canvas: bool = True) -> None:
        """
        Update the canvas size
        :param update_canvas: update the canvas or just calculate the size
        :return: None
        """
        self.canvas_width = ((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH +
                             SMALL_CIRCLE_RADIUS * (self.threads + 1) * 2 + 40 + SHADOW_OFFSET * 2)
        self.canvas_height = (2 * (self.rows - 1) - 1) * DIAMOND_HEIGHT + 2 * DIAMOND_HEIGHT + SHADOW_OFFSET * 2

        if update_canvas:
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            self.toplevel.set_geometry()

    def choose_color(self) -> None:
        """
        Colorchooser for the main color
        :return: None
        """
        color: tuple[tuple[int, int, int], str] | tuple[None, None] = colorchooser.askcolor(initialcolor=self.color,
                                                                                            title="Choose Primary Color"
                                                                                            )
        if color[1]:
            self.set_color(0, color[1])

    def choose_alt_color(self) -> None:
        """
        Colorchooser for the alt color
        :return: None
        """
        color: tuple[tuple[int, int, int], str] | tuple[None, None] = colorchooser.askcolor(
            initialcolor=self.alt_color, title="Choose Secondary Color")
        if color[1]:
            self.set_color(1, color[1])

    def set_color(self, is_alt: bool, fill_color: str | list[int]) -> None:
        """
        Sets the current color
        :param is_alt: set the alt color
        :param fill_color: color
        :return:
        """
        if is_alt:
            self.alt_color = fill_color
            self.alt_colorbtn.set_color(self.alt_color)
        else:
            self.color = fill_color
            self.colorbtn.set_color(self.color)

    def draw_rhombus(self, cx: int, cy: int, w: int, h: int, logical_coords: tuple[float, float],
                     delpoints: list[int] | None = None) -> None:
        """
        Draws a rhombus
        :param cx: x position
        :param cy: y position
        :param w: width
        :param h: height
        :param logical_coords: logical coordinates
        :param delpoints: points to delete
        :return: None
        """
        if delpoints is None:
            delpoints = []
        points: list[int] = [cx, cy - h, cx + w, cy, cx, cy + h, cx - w, cy]
        for i in sorted(delpoints, reverse=True):
            points.pop(i * 2)
            points.pop(i * 2)
        if len(points) <= 4:
            points.append(cx)
            points.append(cy)
        item: int = self.canvas.create_polygon(points, fill="white", outline="black", tags="rhombus")
        self.diamond_ids[item] = (points, cx, cy)
        self.logical_coords[item] = logical_coords

    def draw_grid(self) -> None:
        """
        Draws a grid of rhombuses
        :return: None
        """
        for item in list(self.diamond_ids.keys()):
            if self.canvas.gettags(item) == ("rhombus",):
                self.canvas.delete(item)
                self.diamond_ids.pop(item)

        offset_x: int = 5
        offset_y: int = 5

        delpoints: list[int] = []
        for row in range(self.rows):
            for col in range(self.cols):
                if row == 0:
                    delpoints.append(0)
                if col == 0:
                    delpoints.append(3)
                if col == self.cols - 1:
                    delpoints.append(1)
                cx: int = offset_x + col * 2 * DIAMOND_WIDTH
                cy: int = offset_y + row * 2 * DIAMOND_HEIGHT
                self.draw_rhombus(cx, cy, DIAMOND_WIDTH, DIAMOND_HEIGHT, (col, row), delpoints)
                delpoints = []

        for row in range(self.rows):
            for col in range(self.cols - 1):
                if row == self.rows - 1:
                    delpoints.append(2)
                cx: int = offset_x + col * 2 * DIAMOND_WIDTH + DIAMOND_WIDTH
                cy: int = offset_y + row * 2 * DIAMOND_HEIGHT + DIAMOND_HEIGHT
                self.draw_rhombus(cx, cy, DIAMOND_WIDTH, DIAMOND_HEIGHT, (col + 0.5, row + 0.5), delpoints)
                delpoints = []

        self.draw_circles()

    def draw_circles(self) -> None:
        """
        Draws circles (threads)
        TODO: add customization in Editor
        :return: None
        """
        for item in list(self.circle_ids):
            if self.canvas.gettags(item) == ("circle",):
                self.canvas.delete(item)
                self.circle_ids.pop(item)

        cx: int = (((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH + 20 + SHADOW_OFFSET) +
                   (self.canvas_width - ((2 * (self.cols - 1) - 1) * DIAMOND_WIDTH + 2 * DIAMOND_WIDTH + 20 +
                                         SHADOW_OFFSET * 7.5)) // 2)
        cy: int = ((2 * (self.rows - 1) - 1) * DIAMOND_HEIGHT + 2 * DIAMOND_HEIGHT) // 2

        sub: int = 0

        for i in range(self.threads + 1):
            if i == self.threads // 2:
                sub = 1
                continue
            x: int = cx + (i - self.threads / 2) * SMALL_CIRCLE_RADIUS * 2 + SMALL_CIRCLE_RADIUS
            y: int = cy
            item: int = self.canvas.create_oval(
                x - SMALL_CIRCLE_RADIUS, y - SMALL_CIRCLE_RADIUS,
                x + SMALL_CIRCLE_RADIUS, y + SMALL_CIRCLE_RADIUS,
                fill=self.circle_colors.get(i - sub, "white"), outline="black", tags="circle"
            )
            self.circle_ids[item] = (x, y, i - sub)
            self.circle_colors[i - sub] = self.circle_colors.get(i - sub, "white")

    def update_circles(self) -> None:
        """
        Updates the class
        :return: None
        """
        if self.thread_entry.entry.get() == "":
            self.thread_entry.showmessage("Not defined", fg="red")
            return
        elif self.thread_mode.get() > 35:
            self.thread_entry.showmessage("Too big", fg="red")
            return
        elif self.thread_mode.get() % 2 == 0:
            self.thread_entry.showmessage("Even threads", fg="red")
            return
        else:
            self.thread_entry.delmessage()
        if self.threads != self.thread_mode.get():
            self.threads = self.thread_mode.get()
            self.circle_colors = {}
            self.cols = self.threads // 4 + 1
            self.calc_size()

        self.draw_grid()

    def point_inside_polygon(self, x: int, y: int, poly: list[int]) -> bool:
        """
        Returns if a point is inside a polygon
        :param x: x position
        :param y: y position
        :param poly: polygon points
        :return: whether x, y is inside polygon
        """
        n: int = len(poly)
        inside: bool = False
        p1x: int = poly[0]
        p1y: int = poly[1]
        xinters: int = 0
        for i in range(2, n + 2, 2):
            p2x: int = poly[i % n]
            p2y: int = poly[(i + 1) % n]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def set_rhombus(self, x: float, y: float, color: str | tuple[int, int, int]) -> bool:
        """
        Sets the rhombus at x, y logical coordinates to color
        :param x: x position
        :param y: y position
        :param color: color
        :return: whether the coordinates exist
        """
        if 0 <= x < self.cols - 0.5 and 0 <= y <= self.rows:
            self.canvas.itemconfig(
                list(self.logical_coords.keys())[list(self.logical_coords.values()).index((x, y))], fill=color)
            return True
        return False

    def set_circle(self, n: int, color: str | tuple[int, int, int]) -> None:
        """
        Sets circle n to color
        :param n: circle number
        :param color: color
        :return: None
        """
        self.canvas.itemconfig([i for i, j in self.circle_ids.items() if j[2] == n][0], fill=color)
        self.circle_colors[n] = color

    def fill_circle(self, circle: int, color: str | tuple[int, int, int] = None) -> set[tuple[int, int]]:
        """
        Sets circle and all associated rhombuses to color, if color exists
        :param circle: circle number
        :param color: color
        :return: associated rhombuses
        """
        if color:
            self.set_circle(circle, color)
        rhombuses: set[tuple[int, int]] = set()
        # TODO: add logic using Editor (look at the Kumihimo class for an example)
        return rhombuses

    def get_circle(self, logical_x: float, logical_y: float) -> int:
        """
        Returns the associated circle of a rhombus at logical_x, logical_y
        :param logical_x: x position
        :param logical_y: y position
        :return: associated circle
        """
        for i in range(self.threads):
            if (logical_x, logical_y) in self.fill_circle(i):
                return i
        return 0  # Nothing was found TODO: add error in editor

    def handle_click(self, event: Event, color: str | tuple[int, int, int]) -> None:
        """
        Sets a rhombus or a circle (and associated shapes) to color
        :param event: event from tkinter
        :param color: color
        :return: None
        """
        clicked: tuple[int, ...] = self.canvas.find_closest(event.x, event.y)
        if clicked:
            item_id: int = clicked[0]
            if item_id in self.logical_coords:
                points: list[tuple[int, int]] = self.diamond_ids[item_id][0]
                if not self.point_inside_polygon(event.x, event.y, points):
                    return
                self.fill_circle(self.get_circle(*self.logical_coords[item_id]), color)
            elif item_id in self.circle_ids:
                cx: int = self.circle_ids[item_id][0]
                cy: int = self.circle_ids[item_id][1]
                n: int = self.circle_ids[item_id][2]
                dist: float = math.hypot(event.x - cx, event.y - cy)
                if dist <= SMALL_CIRCLE_RADIUS:
                    self.fill_circle(n, color)

    def on_click_left(self, event: Event) -> None:
        """
        Occurs on left click on the canvas
        :param event: event from tkinter
        :return: None
        """
        self.handle_click(event, self.color)

    def on_click_right(self, event: Event) -> None:
        """
        Occurs on right click on the canvas
        :param event: event from tkinter
        :return: None
        """
        self.handle_click(event, self.alt_color)

    def on_middle_click(self, event: Event) -> None:
        """
        Occurs on middle click on the canvas. Picks the selected shape's color as main or alt (with shift)
        :param event: event from tkinter
        :return: None
        """
        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return

        item_id = clicked[0]

        # Shift key — 0x0001 or 0x0004
        pick_alt = (event.state & 0x0001) != 0 or (event.state & 0x0004) != 0

        if item_id in self.diamond_ids:
            points, _, _ = self.diamond_ids[item_id]
            if self.point_inside_polygon(event.x, event.y, points):
                fill_color = self.canvas.itemcget(item_id, "fill")
                if fill_color:
                    self.set_color(pick_alt, fill_color)

        elif item_id in self.circle_ids:
            cx, cy, _ = self.circle_ids[item_id]
            dist = math.hypot(event.x - cx, event.y - cy)
            if dist <= SMALL_CIRCLE_RADIUS:
                fill_color = self.canvas.itemcget(item_id, "fill")
                if fill_color:
                    self.set_color(pick_alt, fill_color)

    def on_scroll(self, scroll: 1 | -1) -> None:
        """
        Action on scroll
        TODO: add action using Editor
        :param scroll: 1 = up, -1 = down
        :return: None
        """
        pass

    def delete(self) -> None:
        """
        Asks the user if they really want to delete the pattern
        :return: None
        """
        if messagebox.Message(title=self.name, message=f"Are you sure you want to delete {self.name}?", icon="warning",
                              type="yesno").show() == "yes":  # Message used for a yesno warning
            self.toplevel.delete(self)


# Tab for creating a new pattern. May be removed in favor of a menu
class New(Frame):
    """
    Tab for creating a new pattern. May be removed in favor of a menu
    """
    def __init__(self, master: Misc, toplevel: Misc, name: str = "New...", icon: str | None = plus_path,
                 compound: str = "left", *args, **kwargs) -> None:
        """
        Tab for creating a new pattern with the parent MASTER. May be removed in favor of a menu
        :param master: parent
        :param toplevel: toplevel window, usually Window
        :param name: tab name
        :param icon: tab icon
        :param compound: tab compound
        :param args: Frame options
        :param kwargs: Frame options
        """
        super().__init__(master, *args, **kwargs)

        self.toplevel: Misc = toplevel
        self.name: str = name
        self.compound: str = compound

        self.icon: str | None = icon
        if icon is not None:
            self.icon: ImageTk.PhotoImage = geticon(self.icon, True)


# Toplevel window class. Use this or a class with these methods
class Window(Tk):
    """
    Toplevel window class. Use this or a class with these methods
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Toplevel window class. Use this or similar
        :param args: Tk options
        :param kwargs: Tk options
        """
        super().__init__(*args, **kwargs)

        self.title("Fenechki")

        self.min_geometry: tuple[int, int] = (0, 0)

        self.color: str | tuple[int, int, int] = "#ff0000"
        self.alt_color: str | tuple[int, int, int] = "#ffffff"

        self.style: Style = Style()
        self.style.configure("Red.TButton", foreground="red")

        self.notebook: Notebook = Notebook()
        self.notebook.grid(row=0, column=0, sticky="nw")
        self.tabs: list[Custom] = []

        # Not derived from Custom, but will be removed when Custom is complete
        self.tabs.append(Kumihimo(self.notebook, self))
        self.tabs.append(Flat(self.notebook, self))

        # Maybe everything will be stored in one json file
        with open(filenames_path, "r", encoding="utf-8") as f:
            for i in f.readlines()[:-1]:
                self.tabs.append(Custom(self.notebook, self, f"{directory}/{i}"))
        self.tabs.append(New(self.notebook, self))

        for i in self.tabs:
            if i.icon:
                self.notebook.add(i, text=i.name, image=i.icon, compound=i.compound)
            else:
                self.notebook.add(i, text=i.name)

        self.set_geometry(True)

        self.notebook.bind("<<NotebookTabChanged>>",
                           lambda e: self.add_new_tab() if self.notebook.index("current") == len(self.tabs) - 1
                           else None)
        self.bind_all("<Button-1>", lambda e: e.widget.focus_set() if isinstance(e.widget, Widget) else None)

    def set_geometry(self, center: bool = True) -> None:
        """
        Positions the window
        :param center: centers the window
        :return: None
        """
        self.notebook.update()

        self.min_geometry = (self.notebook.winfo_width() + 5, self.notebook.winfo_height() + 5)

        if self.min_geometry[0] > self.winfo_screenwidth():
            self.min_geometry = (self.winfo_screenwidth(), self.min_geometry[1])
            center = True
        if self.min_geometry[1] > self.winfo_screenheight():
            self.min_geometry = (self.min_geometry[0], self.winfo_screenheight())
            center = True

        if center:
            self.geometry(f"{self.min_geometry[0]}x{self.min_geometry[1]}+" +
                          f"{self.winfo_screenwidth() // 2 - self.min_geometry[0] // 2}+" +
                          f"{self.winfo_screenheight() // 2 - self.min_geometry[1] // 2 - 50}")
        else:
            self.geometry(f"{self.min_geometry[0]}x{self.min_geometry[1]}")

    def add_new_tab(self) -> None:
        """
        Adds a new custom tab
        :return: None
        """
        self.tabs.insert(-1, Custom(self.notebook, self))
        if self.tabs[-2].icon:
            self.notebook.insert(len(self.tabs) - 2, self.tabs[-2], text=self.tabs[-2].name, image=self.tabs[-2].icon,
                                 compound=self.tabs[-2].compound)
        else:
            self.notebook.insert(len(self.tabs) - 2, self.tabs[-2], text=self.tabs[-2].name)
        self.notebook.select(len(self.tabs) - 2)
        self.set_geometry()

    def delete(self, obj: Custom) -> None:
        """
        Deletes the tab with obj
        :param obj: instance of Custom to delete
        :return: None
        """
        idx: int = self.tabs.index(obj)
        self.tabs.pop(idx)
        obj.destroy()
        self.notebook.select(idx - 1)
        self.set_geometry()

    def updatetab(self, obj: Custom) -> None:
        """
        Updates the tab with obj
        :param obj: instance of Custom to update
        :return: None
        """
        idx: int = self.tabs.index(obj)
        if obj.icon is not None:
            self.notebook.tab(idx, text=obj.name, image=obj.icon, compound=obj.compound)
        else:
            self.notebook.tab(idx, text=obj.name, image="")


if __name__ == "__main__":
    Window().mainloop()
