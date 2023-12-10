from Audio.AudioPlayer import *

if __name__ == "__main__":
    # Ejemplo de uso
    oalInit()
    audio_file_path = "./data/door.wav"
    player = AudioPlayer(audio_file_path)

    player.play()
    
    try:
        while True:
            # Tu lógica de juego irá aquí
            # Puedes realizar otras operaciones o efectos durante el bucle
            player.set_looping(True)
            player.set_pitch(100.5)
            player.show_effect_buttons
            pass

    except KeyboardInterrupt:
        # Manejamos la interrupción de teclado (Ctrl+C) para salir limpiamente
        pass

    finally:
      print("stop")
      player.stop()
      oalQuit()
      player.destroy()
