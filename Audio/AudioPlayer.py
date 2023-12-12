from openal import *
import pygame
import dearpygui.dearpygui as dpg

class AudioPlayer:
  def __init__(self, file_path, name = "None", listener=None):
    self.source = oalOpen(file_path)
    self.name = name
    self.pitch = 1.0
    self.looping = False
    self.gain = 1.0
    self.doppler = False
    self.factor = 1.0

    self.velocity = (0.0, 0.0, 0.0)
    self.position = (0.0, 0.0, 0.0)
    self.set_doppler_factor(3.0)
    self.listener = listener

    self.is_moving = False
    self.is_cross_fading = False


    if not self.source:
        raise ValueError(f"No se pudo cargar el archivo de sonido: {file_path}")

  def update_listener_position(self):
    if self.listener:
      listener_position = self.listener.get_position()
      listener_orientation = self.listener.get_orientation()
      oalListener().set_position(*listener_position)
      oalListener().set_orientation(*listener_orientation)

  def set_listener(self, listener):
    self.listener = listener

  def play(self):
    if not self.is_playing():
      self.source.play()

  def pause(self):
    self.source.pause()

  def stop(self):
    self.source.stop()
  
  def rewind(self):
    self.source.rewind()

  def destroy(self):
    print("adios")
    #self.source.destroy()
    

  def set_pitch(self, pitch):
    if pitch > 2.0:
      pitch = 2.0
    if pitch < 0.5:
      pitch = 0.5
    self.source.set_pitch(pitch)

  def set_gain(self, gain):
    if gain < 0.0:
      gain = 0.0
    self.gain = gain
    self.source.set_gain(gain)

  def set_position(self, pos):
    self.position = pos
    self.source.set_position(pos)

  def set_velocity(self, x, y, z):
    self.source.set_velocity(x, y, z)

  def set_looping(self, loop):
    self.source.set_looping(loop)

  def set_doppler(self, active):
    self.source.set_doppler(active)

  def set_doppler_factor(self, factor):
    if factor > 10.0:
      factor = 10.0
    if factor < 0.0:
      factor = 0.0
    self.factor = factor
    #self.source.set_doppler_factor(factor)

  def update_source_position(self):
    print("New position x " + str(self.position[0]))
    self.source.set_position((self.position[0], self.position[1], self.position[2]))
  
  def is_playing(self):
    return self.source.get_state() == AL_PLAYING

  def get_pitch(self):
    return self.pitch

  def get_gain(self):
    return self.gain

  def get_position(self):
    return self.position

  def get_velocity(self):
    return self.source.get_velocity()

  def get_looping(self):
    return self.source.get_looping()

  def get_doppler_enabled(self):
    return self.source.get_doppler()

  def get_doppler_factor(self):
    return self.source.get_doppler_factor()

  def get_source_position(self):
    return self.source.get_position()

  def get_name(self):
    return self.name

  def on_pitch_drag(self, sender, app_data):
    self.source.set_pitch(app_data)

  def on_gain_drag(self, sender, app_data):
    self.gain = app_data
    self.set_gain(app_data)

  def on_set_looping(self):
    self.looping = not self.looping
    self.set_looping(self.looping)

  
  def on_drag_velocity_x(self, sender, app_data):
    self.velocity[0] = app_data
    print(self.velocity[0])

  def on_drag_velocity_y(self, sender, app_data):
    self.velocity[1] = app_data
    print(self.velocity[1])

  def on_drag_velocity_z(self, sender, app_data):
    self.velocity[2] = app_data
    print(self.velocity[2])
  
  def on_drag_position_x(self, sender, app_data):
    self.position[0] = app_data
    #print(self.position[0])

  def on_drag_position_y(self, sender, app_data):
    self.position[1] = app_data
    #print(self.position[1])

  def on_drag_position_z(self, sender, app_data):
    self.position[2] = app_data
    #print(self.position[2])

  def on_set_doppler(self):
    self.doppler = not self.doppler
    self.set_doppler(self.doppler)

  def get_state(self):
    state = self.source.get_state()


  def is_stop(self):
    return self.source.get_state() == AL_STOPPED
    #print("Stoped: " + str(AL_STOPPED) + " Paused: " + str(AL_PAUSED) + " Playing: " + str(AL_PLAYING))
  
  def move(self):
    self.is_moving = True
    self.set_position((-10.0, 0.0, 3.0))
    self.play()

  def show_imgui(self, main_dpg, is_gaviota = False):

    with main_dpg.window(label=f"{self.get_name()} Controls"):
      main_dpg.add_button(label=f"Play##{self.get_name()}", callback=self.play)
      main_dpg.add_same_line()
      main_dpg.add_button(label=f"Pause##{self.get_name()}", callback=self.pause)
      main_dpg.add_same_line()
      main_dpg.add_button(label=f"Stop##{self.get_name()}", callback=self.stop)
      main_dpg.add_same_line()
      main_dpg.add_button(label=f"Rewind##{self.get_name()}", callback=self.rewind)
      main_dpg.add_checkbox(label=f"Looping##{self.get_name()}", callback=self.on_set_looping)

      main_dpg.add_text("Effects")
      main_dpg.add_drag_float(label=f"Pitch##{self.get_name()}", default_value=self.get_pitch(), min_value = 0.5, max_value = 2.0, speed = 0.05, callback=lambda sender, app_data: self.on_pitch_drag(sender, app_data))
      main_dpg.add_drag_float(label=f"Gain##{self.get_name()}", default_value=self.get_gain(), min_value = 0.0, max_value = 10.0, speed = 0.05, callback=lambda sender, app_data: self.on_gain_drag(sender, app_data))

      main_dpg.add_checkbox(label=f"Doppler##{self.get_name()}", callback=self.on_set_doppler)

      main_dpg.add_text("Velocity")
      main_dpg.add_drag_float(label=f"Velocity X##{self.get_name()}", default_value=self.velocity[0], speed = 0.5, min_value = -200.0, callback=lambda sender, app_data: self.on_drag_velocity_x(sender, app_data))
      main_dpg.add_drag_float(label=f"Velocity Y##{self.get_name()}", default_value=self.velocity[1], speed = 0.5, callback=lambda sender, app_data: self.on_drag_velocity_y(sender, app_data))
      main_dpg.add_drag_float(label=f"Velocity Z##{self.get_name()}", default_value=self.velocity[2], speed = 0.5, callback=lambda sender, app_data: self.on_drag_velocity_z(sender, app_data))
     
      main_dpg.add_text("Position")
      main_dpg.add_drag_float(label=f"Position X##{self.get_name()}", default_value=self.position[0], speed = 0.5, min_value = -200.0, callback=lambda sender, app_data: self.on_drag_position_x(sender, app_data))
      main_dpg.add_drag_float(label=f"Position Y##{self.get_name()}", default_value=self.position[1], speed = 0.5, callback=lambda sender, app_data: self.on_drag_position_y(sender, app_data))
      main_dpg.add_drag_float(label=f"Position Z##{self.get_name()}", default_value=self.position[2], speed = 0.5, callback=lambda sender, app_data: self.on_drag_position_z(sender, app_data))

      if is_gaviota == True:
        main_dpg.add_button(label=f"Move##{self.get_name()}", callback=self.move)

    """
          
        if ImGui.CollapsingHeader("Doppler"):
          doppler_enabled = self.get_doppler_enabled()
          if ImGui.Checkbox(f"Enabled##{self.get_name()}", doppler_enabled):
            self.set_doppler(doppler_enabled)

          if doppler_enabled:
            doppler_factor = self.get_doppler_factor()
            if ImGui.DragFloat(f"Doppler Factor##{self.get_name()}", doppler_factor, 0.1, 0.0):
              self.set_doppler_factor(doppler_factor)
    """