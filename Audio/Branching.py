from Audio.AudioPlayer import *

class Branching:

  def __init__(self):
    self._a_songs = []
    for i in range(1, 9):
      self._a_songs.append(AudioPlayer(f"data/branching/slbgm_forest_A-0{i}.ogg"))
    self._b_songs = []
    for i in range(1, 9):
      self._b_songs.append(AudioPlayer(f"data/branching/slbgm_forest_B-0{i}.ogg"))
    self._ab_songs = []
    for i in range(1, 3):
      self._ab_songs.append(AudioPlayer(f"data/branching/slbgm_forest_AB-0{i}.ogg"))
    self._ba_songs = []
    for i in range(1, 3):
      self._ba_songs.append(AudioPlayer(f"data/branching/slbgm_forest_BA-0{i}.ogg"))
    self._song_list = 'A'
    self._aIndex = 0
    self._bIndex = 0
    self._abIndex = 0
    self._baIndex = 0

  def update(self):
    if (self._song_list == 'A'):
      if (self._a_songs[self._aIndex].is_playing() == False):
        self._aIndex += 1
        self._aIndex %= len(self._a_songs)
        self._a_songs[self._aIndex].set_gain(0.01)
        self._a_songs[self._aIndex].play()
    
    if (self._song_list == 'B'):
      if (self._b_songs[self._bIndex].is_playing() == False):
        self._bIndex += 1
        self._bIndex %= len(self._b_songs)
        self._b_songs[self._bIndex].set_gain(0.01)
        self._b_songs[self._bIndex].play()

    if (self._song_list == 'AB'):
      if (self._ab_songs[self._abIndex].is_playing() == False):
        self._song_list = 'B'

    if (self._song_list == 'BA'):
      if (self._ba_songs[self._baIndex].is_playing() == False):
        self._baIndex += 1
        self._baIndex %= len(self._ba_songs)
        self._ba_songs[self._baIndex].set_gain(0.01)
        self._ba_songs[self._baIndex].play()
    

  def change_state(self):
    self._change_state = True
