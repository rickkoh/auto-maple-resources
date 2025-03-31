"""A collection of all commands that a Kanna can use to interact with the game."""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

# List of key mappings
class Key:
    # Movement
    JUMP = 'space'

    # Buffs
    DECENT_SHARP_EYES = '1'
    DECENT_HOLY_SYMBOL = '2'
    DECENT_HYPER_BODY = '3'
    ROLL_OF_THE_DICE = '4'
    LOADED_DICE = '5'
    ELEMENTAL_INFUSION = '6'
    STATIC_CHARGE = '7'
    CYGNUS_KNIGHTS = 'q'
    SPEED_INFUSION = 'w'
    GLORY_OF_GUARDIANS = 'e'
    EXTREME_BLITZ = 'r'

    # Skills
    THUNDEROUS_DIVE = 'z'
    RISING_WAVE = 'x'
    CRASHING_WAVE = 'c'
    FLASH = 'v'
    RELENTLESS_FURY = 'a'
    WHIRLWIND = 's'
    BOLT_ANCHOR = 'd'
    ANNIHILATION = 'f'
    TIDAL_WAVE = 'g'
    SHARK_MISSILE = 'shift'

#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.5:
        if direction == 'down':
            press(Key.JUMP, 3)
        elif direction == 'up':
            press(Key.JUMP, 1)
    FlashJump().main()


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        UpJump().main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    """Uses each of Striker's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.elemental_infusion_on = False
        self.static_charge_on = False
        self.loaded_dice = -1
        self.buff_time = 0
        self.glory_of_guardians_cd = 0
        self.extreme_blitz_cd = 0

    def main(self):
        buffs = [
            # Key.DECENT_SHARP_EYES,
            # Key.DECENT_HOLY_SYMBOL,
            # Key.DECENT_HYPER_BODY,
            Key.ROLL_OF_THE_DICE,
            Key.CYGNUS_KNIGHTS,
            Key.SPEED_INFUSION,
            # Key.GLORY_OF_GUARDIANS,
            # Key.EXTREME_BLITZ
        ]
        now = time.time()
        if not self.loaded_dice == 6:
            press(Key.LOADED_DICE, 1, up_time=0.5)
            press('6', 1)
            self.loaded_dice = 6
        if not self.elemental_infusion_on:
            press(Key.ELEMENTAL_INFUSION, 1, up_time=utils.rand_float(0.6, 0.7))
            self.elemental_infusion_on = True
        if not self.static_charge_on:
            press(Key.STATIC_CHARGE, 1, up_time=utils.rand_float(0.2, 0.25))
            self.static_charge_on = True
        if self.glory_of_guardians_cd == 0 or now - self.glory_of_guardians_cd > 120:
            press(Key.GLORY_OF_GUARDIANS, 1, up_time=utils.rand_float(0.6, 0.7))
            self.glory_of_guardians_cd = now
        if self.extreme_blitz_cd == 0 or now - self.extreme_blitz_cd > 120:
            press(Key.EXTREME_BLITZ, 1, up_time=utils.rand_float(0.6, 0.7))
            self.extreme_blitz_cd = now
        if self.buff_time == 0 or now - self.buff_time > settings.buff_cooldown:
            for key in buffs:
                press(key, 2, up_time=utils.rand_float(0.2, 0.3))
            self.buff_time = now


class FlashJump(Command):
    """Performs a Flash Jump in the specified direction."""

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)
        
    def main(self):
        if self.direction:
            key_down(self.direction)
            time.sleep(0.05)
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.16, 0.17))
        press(Key.JUMP, 1)
        if self.direction:
            key_up(self.direction)


class UpJump(Command):
    """Performs a jump in the upward direction."""

    def main(self):
        key_down('up')
        time.sleep(0.05)
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.1, 0.2))
        press(Key.JUMP, 1)
        key_up('up')


class NormalJump(Command):
    """Perform a normal jump"""

    def main(self):
        key_down(Key.JUMP)


class ThunderousDive(Command):
    """Attacks using 'ThunderousDive' in a given direction."""

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            key_down(self.direction)
            time.sleep(0.05)
        press(Key.THUNDEROUS_DIVE, 1, down_time=0.02, up_time=0.02)
        if self.direction:
            key_up(self.direction)


class RisingWave(Command):
    """Attacks using 'RisingWave' in a given direction."""

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            key_down(self.direction)
            time.sleep(0.05)
        press(Key.RISING_WAVE, 1, down_time=0.02, up_time=0.02)
        if self.direction:
            key_up(self.direction)


class CrashingWave(Command):
    """Attacks using 'CrashingWave'."""

    def main(self):
        press(Key.CRASHING_WAVE, 1)


class Flash(Command):
    """Attacks using 'Flash'."""

    def main(self):
        press(Key.FLASH, 1)


class RelentlessFury(Command):
    """Attacks using 'RelentlessFury'."""
    
    def main(self):
        press(Key.RELENTLESS_FURY, 1)


class Whirlwind(Command):
    """Attacks using 'Whirlwind'."""

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)
        self.cooldown = 0

    def main(self):
        now = time.time()
        if self.cooldown == 0 or now - self.cooldown > 12:
            if self.direction:
                key_down(self.direction)
                time.sleep(0.05)
            press(Key.WHIRLWIND, 1)
            if self.direction:
                key_up(self.direction)
            self.cooldown = now



class BoltAnchor(Command):
    """Attacks using 'BoltAnchor'."""

    def main(self):
        press(Key.BOLT_ANCHOR, 1)


class Annihilation(Command):
    """Attacks using 'Annihilation'."""
    
    def main(self):
        press(Key.ANNIHILATION, 1)


class TidalWave(Command):
    """Attacks using 'TidalWave'."""

    def __init__(self):
        super().__init__(locals())
        self.cooldown = 0
    
    def main(self):
        now = time.time()
        if self.cooldown == 0 or now - self.cooldown > 45:
            press(Key.TIDAL_WAVE, 1)
            self.cooldown = now


class SharkMissile(Command):
    """Attacks using 'SharkMissile' in a given direction."""

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)
        self.cooldown = 0

    def main(self):
        now = time.time()
        if self.cooldown == 0 or now - self.cooldown > 8:
            if self.direction:
                key_down(self.direction)
                time.sleep(0.05)
            press(Key.SHARK_MISSILE, 1)
            if self.direction:
                key_up(self.direction)
            self.cooldown = now
