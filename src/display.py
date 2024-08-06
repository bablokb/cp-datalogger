#-----------------------------------------------------------------------------
# Manage update of display.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import board
import pins
from log_writer import Logger

import displayio
from dataviews.DisplayFactory import DisplayFactory

g_logger = Logger()

CHAR_BAT_FULL  = "\u25AE"    # black vertical rectangle
CHAR_BAT_EMPTY = "\u25AF"    # white vertical rectangle
CHAR_WARN      = "\u26A0"    # warning sign

class Display:
  """ prepare and update display for the datalogger """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config,spi):
    """ constructor """

    self._config = config
    self._spi    = spi
    self._view   = None
    self.strobe_wait = getattr(config,"DISPLAY_STROBE_WAIT",3)

    # maybe use builtin display?
    if config.HAVE_DISPLAY == "internal":
      if hasattr(pins,"DISPLAY"):
        self._display = pins.DISPLAY()    # MUST be a method
      else:
        self._display = board.DISPLAY     # no method
      if hasattr(self._display,"auto_refresh"):
        self._display.auto_refresh = False
      return

    # spi - if not already created
    if not self._spi:
      import busio
      self._spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI)

    displayio.release_displays()
    if config.HAVE_DISPLAY == "Inky-Pack":
      self._display = DisplayFactory.inky_pack(self._spi)
    elif config.HAVE_DISPLAY == "Inky-pHat":
      self._display = DisplayFactory.inky_phat(
        pin_dc=pins.PIN_INKY_DC,pin_cs=pins.PIN_INKY_CS,
        pin_rst=pins.PIN_INKY_RST,pin_busy=pins.PIN_INKY_BUSY,spi=self._spi)
      if not hasattr(config,"DISPLAY_STROBE_WAIT"):
        self.strobe_wait = 6
    elif config.HAVE_DISPLAY == "Ada-2.13-Mono":
      self._display = DisplayFactory.ada_2_13_mono(
        pin_dc=pins.PIN_INKY_DC,pin_cs=pins.PIN_INKY_CS,
        pin_rst=pins.PIN_INKY_RST,pin_busy=pins.PIN_INKY_BUSY,spi=self._spi)
    elif config.HAVE_DISPLAY == "Ada-1.54-Mono":
      self._display = DisplayFactory.ada_1_54_mono(
        pin_dc=pins.PIN_INKY_DC,pin_cs=pins.PIN_INKY_CS,
        pin_rst=pins.PIN_INKY_RST,pin_busy=pins.PIN_INKY_BUSY,spi=self._spi)
    elif config.HAVE_DISPLAY == "Display-Pack":
      self._display = DisplayFactory.display_pack(self._spi)
      self._display.auto_refresh = False
    else:
      g_logger.print(f"unsupported display: {config.HAVE_DISPLAY}")
      config.HAVE_DISPLAY = None

  # --- return display-object   -----------------------------------------------

  def get_display(self):
    """ return display-object """
    return self._display

  # --- create view   ---------------------------------------------------------

  def create_view(self,formats):
    """ create data-view """

    if self._view:
      return

    g_logger.print("start: _create_view")

    from dataviews.Base import Color, Justify
    from dataviews.DataView  import DataView
    from dataviews.DataPanel import DataPanel, PanelText

    # guess best dimension
    n_formats = len(formats)
    if n_formats < 5:
      dim = (2,2)
    elif n_formats < 7:
      dim = (3,2)
    else:
      dim = (3,4)

    if n_formats < dim[0]*dim[1]:
      formats.extend(
        ["" for _ in range(dim[0]*dim[1] - n_formats)])
    elif n_formats > dim[0]*dim[1]:
      g_logger.print(f"only displaying first {dim[0]*dim[1]/2:.0f} sensor-values")
      del formats[dim[0]*dim[1]:]

    border  = 1
    offset  = 1    # keep away from border-pixels
    divider = 1
    padding = 5
    self._view = DataView(
      dim=dim,
      width=self._display.width-2*(border+padding+offset)-(dim[1]-1)*divider,
      height=int(0.6*self._display.height),
      justify=Justify.LEFT,
      fontname=f"fonts/{self._config.FONT_DISPLAY}.bdf",
      formats=formats,
      border=border,
      divider=divider,
      color=Color.BLACK,
      bg_color=Color.WHITE
    )

    for i in range(0,dim[0]*dim[1],2):
      self._view.justify(Justify.LEFT,index=i)
      self._view.justify(Justify.RIGHT,index=i+1)

    # create DataPanel
    title = PanelText(text=f"{self._config.LOGGER_TITLE}",
                      fontname=f"fonts/{self._config.FONT_DISPLAY}.bdf",
                      justify=Justify.CENTER)

    self._footer = PanelText(text=f"Updated: ",
                             fontname=f"fonts/{self._config.FONT_DISPLAY}.bdf",
                             justify=Justify.RIGHT)
    self._panel = DataPanel(
      x = offset,
      y = offset,
      width=self._display.width-2*offset,
      height=self._display.height-2*offset,
      view=self._view,
      title=title,
      footer=self._footer,
      border=border,
      padding=5,
      justify=Justify.CENTER,
      color=Color.BLACK,
      bg_color=Color.WHITE
    )
    self._display.root_group = self._panel

    g_logger.print("end:  _create_view")

  # --- get status-text   ----------------------------------------------------

  def _get_status(self,app):
    """ get text of status line """

    dt, ts = app.data['ts_str'].split("T")
    bat_level = app.data['battery']
    if app.with_lipo:
      warn_level = getattr(self._config,"LIPO_WARN",3.2)
    else:
      warn_level = getattr(self._config,"BAT_WARN",2.2)

    if bat_level <= warn_level:
      bat_status = f"{CHAR_WARN}{CHAR_BAT_EMPTY}"
    else:
      bat_status = f" {CHAR_BAT_FULL}"

    return f"at {dt} {ts} {app.sd_status}{app.lora_status} {bat_status}"

  # --- set values for ui   --------------------------------------------------

  def set_values(self,app):
    """ set values """

    if len(app.values) < len(app.formats):
      # fill in unused cells
      app.values.extend(
        [None for _ in range(len(app.formats)-len(app.values))])
    elif len(app.values) > len(app.formats):
      # remove extra values
      del app.values[len(app.formats):]

    # set footer
    self._footer.text = self._get_status(app)
    # set values
    self._view.set_values(app.values)

  # --- refresh the display   ------------------------------------------------

  def refresh(self):
    """ refresh display """
    self._display.refresh()

  # --- create simple ui   ---------------------------------------------------

  def create_simple_view(self):
    """ create simple view of a single DisplayText """

    if self._view:
      return

    g_logger.print("start: _create_simple_view")

    from adafruit_bitmap_font import bitmap_font
    from adafruit_display_text import label as label
    from vectorio import Rectangle

    font = bitmap_font.load_font(f"fonts/{self._config.FONT_DISPLAY}.bdf")
    self._view = displayio.Group()
    shader = displayio.Palette(2)
    shader[0] = 0xFFFFFF
    shader[1] = 0x000000
    self._view.append(Rectangle(pixel_shader=shader,x=0,y=0,
                   width=self._display.width,
                   height=self._display.height,
                   color_index=0))
    m = label.Label(text="ABCD: 23.5",font=font)         # 10 chars
    self._max_chars = 10*self._display.width/m.width      # round later
    self._panel = label.Label(font=font,color=shader[1],
                              tab_replacement=(2," "),
                              line_spacing=1,
                              text=60*'M',anchor_point=(0.5,0.5))
    self._panel.anchored_position = (self._display.width/2,
                                     self._display.height/2)
    self._view.append(self._panel)
    self._display.root_group = self._view
    g_logger.print("end:   _create_simple_view")

  # --- set ui-text for simple-ui   ------------------------------------------

  def set_ui_text(self,app):
    """ set text of simple UI """

    # create dynamic format: width of label is widh - 4 - 1 (4:value, 1:colon)
    # layout is four columns: label:value label:value
    w = int((self._max_chars-1)/2)
    template1 = "{label:<"+f"{w-5}.{w-5}"+"}:{value:>4.4}"
    template2 = "{label:<"+f"{w-4}.{w-4}"+"}:{value:>4.4}"
    columns = app.csv_header.split('#')[-1].split(',')
    merged = zip(columns,app.record.split(','))

    # collect output into string
    ui_string = f"{self._config.LOGGER_TITLE}"
    ui_line = ""

    for label,value in merged:
      if "°" in label:
        # workaround for CP bug (issue #8171)
        template = template2
      else:
        template = template1
      if label == "ts":
        ts_line = f"\n{self._get_status(app)}"
      elif label == "ID":
        pass                 # skip ID (should be part of title)
      elif ui_line:          # second column
        ui_string += f"\n{ui_line} "+template.format(label=label,value=value)
        ui_line = ""
      else:
        ui_line = template.format(label=label,value=value)

    if ui_line:
      ui_string += f"\n{ui_line}"
    ui_string += ts_line
    g_logger.print(ui_string)
    self._panel.text = ui_string
