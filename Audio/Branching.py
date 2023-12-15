from Audio.AudioPlayer import *

# Definition of the Branching class
class Branching:

  def __init__(self):
    self.volume = 0.02
    self._a_songs = []
    for i in range(1, 9):
      self._a_songs.append(AudioPlayer(f"data/branching/slbgm_forest_A-0{i}.ogg", name=f"slbgm_forest_A-0{i}"))
    self._b_songs = []
    for i in range(1, 9):
      self._b_songs.append(AudioPlayer(f"data/branching/slbgm_forest_B-0{i}.ogg", name=f"slbgm_forest_B-0{i}"))
    self._ab_songs = []
    for i in range(1, 3):
      self._ab_songs.append(AudioPlayer(f"data/branching/slbgm_forest_AB-0{i}.ogg", name=f"slbgm_forest_AB-0{i}"))
    self._ba_songs = []
    for i in range(1, 3):
      self._ba_songs.append(AudioPlayer(f"data/branching/slbgm_forest_BA-0{i}.ogg", name=f"slbgm_forest_BA-0{i}"))
    self._song_list = 'A'
    self._aIndex = 0
    self._bIndex = 0
    self._abIndex = 0
    self._baIndex = 0
    self._change_state = False

  def is_chill(self):
    """
    Check if the current state is a 'chill' state (A or BA)
    """
    return self._song_list == 'A' or self._song_list == 'BA'

  def update(self):
    """
    Update the state of the Branching object
    """
    if (self._song_list == 'A'):
      if (self._a_songs[self._aIndex].is_playing() == False):
        if (self._change_state == True):
          self._change_state = False
          self._song_list = 'AB'
          if (self._aIndex > 3):
            self._abIndex = 1
            self._ab_songs[self._abIndex].set_gain(self.volume)
            self._ab_songs[self._abIndex].play()
          else:
            self._abIndex = 0
            self._ab_songs[self._abIndex].set_gain(self.volume)
            self._ab_songs[self._abIndex].play()
        else:
          self._aIndex += 1
          self._aIndex %= len(self._a_songs)
          self._a_songs[self._aIndex].set_gain(self.volume)
          self._a_songs[self._aIndex].play()
    
    if (self._song_list == 'B'):
      if (self._b_songs[self._bIndex].is_playing() == False):
        if (self._change_state == True):
          self._change_state = False
          self._song_list = 'BA'
          if (self._bIndex > 3):
            self._baIndex = 1
            self._ba_songs[self._baIndex].set_gain(self.volume)
            self._ba_songs[self._baIndex].play()
          else:
            self._baIndex = 0
            self._ba_songs[self._baIndex].set_gain(self.volume)
            self._ba_songs[self._baIndex].play()
        else:
          self._bIndex += 1
          self._bIndex %= len(self._b_songs)
          self._b_songs[self._bIndex].set_gain(self.volume)
          self._b_songs[self._bIndex].play()

    if (self._song_list == 'AB'):
      if (self._ab_songs[self._abIndex].is_playing() == False):
        self._song_list = 'B'
        if (self._aIndex > 3):
          self._bIndex = 5
          self._b_songs[self._bIndex].set_gain(self.volume)
          self._b_songs[self._bIndex].play()
        else:
          self._bIndex = 0
          self._b_songs[self._bIndex].set_gain(self.volume)
          self._b_songs[self._bIndex].play()

    if (self._song_list == 'BA'):
      if (self._ba_songs[self._baIndex].is_playing() == False):
        self._song_list = 'A'
        if (self._bIndex > 3):
          self._aIndex = 5
          self._a_songs[self._aIndex].set_gain(self.volume)
          self._a_songs[self._aIndex].play()
        else:
          self._aIndex = 0
          self._a_songs[self._aIndex].set_gain(self.volume)
          self._a_songs[self._aIndex].play()
    

  def change_state(self):
    """
    Trigger a state change
    """
    self._change_state = True

  def __str__(self):
    """
    String representation of the current state
    """
    if (self._song_list == 'A'):
      return self._a_songs[self._aIndex].get_name()
    if (self._song_list == 'B'):
      return self._b_songs[self._bIndex].get_name()
    if (self._song_list == 'AB'):
      return self._ab_songs[self._abIndex].get_name()
    if (self._song_list == 'BA'):
      return self._ba_songs[self._baIndex].get_name()
    
  def get_nex_song(self):
    if (self._song_list == 'A'):
      if (self._change_state == True):
        if (self._aIndex > 3):
          return self._ab_songs[1].get_name()
        else:
          return self._ab_songs[0].get_name()
      else:
        return self._a_songs[self._aIndex + 1 % len(self._a_songs)].get_name()
    
    if (self._song_list == 'B'):
      if (self._change_state == True):
        if (self._bIndex > 3):
          return self._ba_songs[1].get_name()
        else:
          return self._ba_songs[0].get_name()
      else:
        return self._b_songs[self._bIndex + 1 % len(self._b_songs)].get_name()

    if (self._song_list == 'AB'):
      if (self._aIndex > 3):
        return self._b_songs[5].get_name()
      else:
        return self._b_songs[0].get_name()

    if (self._song_list == 'BA'):
        if (self._bIndex > 3):
          return self._a_songs[5].get_name()
        else:
          return self._a_songs[0].get_name()
  