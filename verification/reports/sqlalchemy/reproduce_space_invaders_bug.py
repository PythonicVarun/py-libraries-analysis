import sys
from unittest.mock import MagicMock

# Mocking curses since it's environment dependent
sys.modules['curses'] = MagicMock()

def reproduce_space_invaders_bug():
    print("Simulating Space Invaders global variable issue...")
    
    # This mimics the structure of the example where _COLOR_PAIRS 
    # is used before/without proper module-level declaration
    
    class Glyph:
        def draw(self, color):
            # Line 164 in the original file
            try:
                return _COLOR_PAIRS[color]
            except NameError as e:
                print(f"Caught expected NameError: {e}")
                return None

    def main_init():
        global _COLOR_PAIRS
        _COLOR_PAIRS = {1: "red", 2: "green"}
        print("Initialized _COLOR_PAIRS")

    g = Glyph()
    print("Calling draw() before init...")
    g.draw(1)
    
    main_init()
    print("Calling draw() after init...")
    val = g.draw(1)
    print(f"Result: {val}")

if __name__ == "__main__":
    reproduce_space_invaders_bug()
