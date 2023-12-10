from openal import *

class AudioPlayer:
  def __init__(self, file_path, name = "None"):
    self.source = oalOpen(file_path)
    self.name = name
    if not self.source:
        raise ValueError(f"No se pudo cargar el archivo de sonido: {file_path}")

  def play(self):
    if not self.is_playing():
      self.source.play()

  def stop(self):
    self.source.stop()

  def destroy(self):
    self.source.destroy()
    

  def set_pitch(self, pitch):
    if pitch > 2.0:
      pitch = 2.0
    if pitch < 0.5:
      pitch = 0.5
    self.source.set_pitch(pitch)

  def set_gain(self, gain):
    if gain < 0.0:
      gain = 0.0
    self.source.set_gain(gain)

  def set_position(self, x, y, z):
    self.source.set_position(x, y, z)

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
    self.source.set_doppler_factor(factor)

  def update_source_position(self, x, y, z):
    self.source.update_position(x, y, z)
  
  def is_playing(self):
    return self.source.get_state() == AL_PLAYING

  def get_pitch(self):
    return self.source.get_pitch()

  def get_gain(self):
    return self.source.get_gain()

  def get_position(self):
    return self.source.get_position()

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
    if self.name != "None":
      return self.source.get_name()
    else:
      return self.name
  
  def show_effect_buttons(self):
    if ImGui.CollapsingHeader(f"{self.get_name()} Controls"):
      if ImGui.Button(f"Play##{self.get_name()}"):
        self.play()
      ImGui.SameLine()
      if ImGui.Button(f"Pause##{self.get_name()}"):
          self.pause()
      ImGui.SameLine()
      if ImGui.Button(f"Resume##{self.get_name()}"):
          self.resume()
      ImGui.SameLine()
      if ImGui.Button(f"Stop##{self.get_name()}"):
          self.stop()
      
      if ImGui.CollapsingHeader(f"{self.get_name()} Effects"):
        pitch = self.get_pitch()
        if ImGui.DragFloat(f"Pitch##{self.get_name()}", pitch, 0.05, 0.5, 2.0):
            self.set_pitch(pitch)

        looping = self.get_looping()
        if ImGui.Checkbox(f"Looping##{self.get_name()}", looping):
          self.set_looping(looping)

        velocity = self.get_velocity()
        if ImGui.DragFloat3(f"Velocity##{self.get_name()}", velocity, 0.1, 0.0):
          self.set_velocity(velocity)
        
        position = self.get_position()
        if ImGui.DragFloat3(f"Position##{self.get_name()}", position, 0.1, 0.0):
          self.set_position(position)
        
        gain = self.get_gain()
        if ImGui.DragFloat(f"Gain##{self.get_name()}", gain, 0.1, 0.0):
          self.set_gain(gain)
          
        if ImGui.CollapsingHeader("Doppler"):
          doppler_enabled = self.get_doppler_enabled()
          if ImGui.Checkbox(f"Enabled##{self.get_name()}", doppler_enabled):
            self.set_doppler(doppler_enabled)

          if doppler_enabled:
            doppler_factor = self.get_doppler_factor()
            if ImGui.DragFloat(f"Doppler Factor##{self.get_name()}", doppler_factor, 0.1, 0.0):
              self.set_doppler_factor(doppler_factor)
