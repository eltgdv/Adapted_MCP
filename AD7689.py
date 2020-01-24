import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

class AD7689(object):
	"""Class to represent an AD7689 analog to digital converter."""
	
    def __init__(self, clk=None, cs=None, miso=None, mosi=None, spi=None, gpio=None):
        """Initialize MAX31855 device with software SPI on the specified CLK, CS, and DO pins.  Alternatively can specify hardware SPI by sending an Adafruit_GPIO.SPI.SpiDev device in the spi parameter."""
        self._spi = None
        # Handle hardware SPI
        if spi is not None:
            self._spi = spi
        elif clk is not None and cs is not None and miso is not None and mosi is not None:
            # Default to platform GPIO if not provided.
            if gpio is None:
                gpio = GPIO.get_platform_gpio()
            self._spi = SPI.BitBang(gpio, clk, mosi, miso, cs)
        else:
            raise ValueError('Must specify either spi for for hardware SPI or clk, cs, miso, and mosi for software SPI!')
        self._spi.set_clock_hz(1000000)
        self._spi.set_mode(0)
        self._spi.set_bit_order(SPI.MSBFIRST)
		
    def read_adc(self, adc_number):
        """Read the current value of the specified ADC channel (0-7).  The values can range from 0 to 65536 (16-bits)."""
        assert 0 <= adc_number <= 7, 'ADC number must be a value of 0-7!'
        # Build a single channel read command.
        
        command = 0b1 << 3 # First bit Configuration update
        command = (command + 0b111) << 3  # Input channel configuration 
        command = (command + adc_number) << 1 # Input channel selection
        command = (command + 0b1) << 3 # bandwith low pass filter
        command = (command + 0b001) << 2 # Refrence/buffer selection
        command = (command + 0b00) << 1 # Channel sequencer
        command = (command + 0b1) # Read back the CFG register
        
        resp = self._spi.transfer([command, 0x0, 0x0])
        
        # Parse out the 16 bits of response data and return it.
        result = (resp[0] & 0x01) << 9
        result |= (resp[1] & 0xFF) << 1
        result |= (resp[2] & 0x80) >> 7
        return result & 0x10000