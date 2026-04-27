"""
Custom date/time utilities (minimal implementation).
"""


class DateTime:
    """Simple datetime representation."""
    
    MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0):
        """Initialize datetime."""
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
    
    @classmethod
    def now(cls):
        """Get current datetime (using system clock)."""
        import time
        lt = time.localtime()
        return cls(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
    
    def strftime(self, fmt: str) -> str:
        """Format datetime as string."""
        result = []
        i = 0
        while i < len(fmt):
            if fmt[i] == '%' and i + 1 < len(fmt):
                directive = fmt[i + 1]
                if directive == 'Y':
                    result.append(str(self.year))
                elif directive == 'm':
                    result.append(f"{self.month:02d}")
                elif directive == 'd':
                    result.append(f"{self.day:02d}")
                elif directive == 'H':
                    result.append(f"{self.hour:02d}")
                elif directive == 'M':
                    result.append(f"{self.minute:02d}")
                elif directive == 'S':
                    result.append(f"{self.second:02d}")
                elif directive == 'B':
                    result.append(self.MONTH_NAMES[self.month - 1])
                elif directive == 'b':
                    result.append(self.MONTH_NAMES[self.month - 1][:3])
                elif directive == 'A':
                    result.append(self._get_day_name())
                elif directive == 'a':
                    result.append(self._get_day_name()[:3])
                elif directive == '%':
                    result.append('%')
                else:
                    result.append('%')
                    result.append(directive)
                i += 2
            else:
                result.append(fmt[i])
                i += 1
        return ''.join(result)
    
    def isoformat(self) -> str:
        """Return ISO format string."""
        return (f"{self.year:04d}-{self.month:02d}-{self.day:02d}T"
                f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}")
    
    def _get_day_name(self) -> str:
        """Get day name (simplified, may not be 100% accurate)."""
        # Use Zeller's congruence to find day of week
        month = self.month
        year = self.year
        
        if month < 3:
            month += 12
            year -= 1
        
        q = self.day
        m = month
        k = year % 100
        j = year // 100
        
        h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
        
        # Convert to day of week (h: 0=Sat, 1=Sun, 2=Mon, etc.)
        day_index = (h + 5) % 7
        return self.DAY_NAMES[day_index]
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.isoformat()
    
    def __repr__(self) -> str:
        """Return representation."""
        return f"DateTime({self.year}, {self.month}, {self.day}, {self.hour}, {self.minute}, {self.second})"


def get_current_datetime_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get current datetime as formatted string."""
    dt = DateTime.now()
    return dt.strftime(fmt)


def get_current_datetime_iso() -> str:
    """Get current datetime in ISO format."""
    dt = DateTime.now()
    return dt.isoformat()
