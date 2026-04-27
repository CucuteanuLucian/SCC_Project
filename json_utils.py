"""
Custom JSON serialization/deserialization (minimal implementation).
"""
from typing import Any, Dict, List


class JSONEncoder:
    """Simple JSON encoder for basic types."""
    
    @staticmethod
    def encode(obj: Any) -> str:
        """Encode object to JSON string."""
        return JSONEncoder._encode_value(obj)
    
    @staticmethod
    def _encode_value(obj: Any) -> str:
        """Encode a value recursively."""
        if obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif isinstance(obj, str):
            return JSONEncoder._encode_string(obj)
        elif isinstance(obj, dict):
            return JSONEncoder._encode_dict(obj)
        elif isinstance(obj, (list, tuple)):
            return JSONEncoder._encode_list(obj)
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    @staticmethod
    def _encode_string(s: str) -> str:
        """Encode string with proper escaping."""
        # Escape special characters
        s = s.replace("\\", "\\\\")
        s = s.replace('"', '\\"')
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        s = s.replace("\t", "\\t")
        return f'"{s}"'
    
    @staticmethod
    def _encode_dict(d: Dict) -> str:
        """Encode dictionary."""
        items = []
        for key, value in d.items():
            encoded_key = JSONEncoder._encode_string(str(key))
            encoded_value = JSONEncoder._encode_value(value)
            items.append(f"{encoded_key}: {encoded_value}")
        return "{" + ", ".join(items) + "}"
    
    @staticmethod
    def _encode_list(lst: List) -> str:
        """Encode list."""
        items = [JSONEncoder._encode_value(item) for item in lst]
        return "[" + ", ".join(items) + "]"


class JSONDecoder:
    """Simple JSON decoder for basic types."""
    
    def __init__(self, text: str):
        """Initialize decoder."""
        self.text = text
        self.pos = 0
    
    def decode(self) -> Any:
        """Decode JSON string."""
        self._skip_whitespace()
        value = self._decode_value()
        self._skip_whitespace()
        if self.pos < len(self.text):
            raise ValueError(f"Extra data after JSON at position {self.pos}")
        return value
    
    def _decode_value(self) -> Any:
        """Decode a value recursively."""
        self._skip_whitespace()
        
        if self.pos >= len(self.text):
            raise ValueError("Unexpected end of JSON")
        
        char = self.text[self.pos]
        
        if char == '"':
            return self._decode_string()
        elif char == '{':
            return self._decode_dict()
        elif char == '[':
            return self._decode_list()
        elif char == 't':
            return self._decode_true()
        elif char == 'f':
            return self._decode_false()
        elif char == 'n':
            return self._decode_null()
        elif char == '-' or char.isdigit():
            return self._decode_number()
        else:
            raise ValueError(f"Unexpected character '{char}' at position {self.pos}")
    
    def _decode_string(self) -> str:
        """Decode string."""
        if self.text[self.pos] != '"':
            raise ValueError("Expected '\"'")
        
        self.pos += 1
        result = []
        
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            char = self.text[self.pos]
            
            if char == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    raise ValueError("Unexpected end of string")
                
                next_char = self.text[self.pos]
                if next_char == '"':
                    result.append('"')
                elif next_char == '\\':
                    result.append('\\')
                elif next_char == '/':
                    result.append('/')
                elif next_char == 'b':
                    result.append('\b')
                elif next_char == 'f':
                    result.append('\f')
                elif next_char == 'n':
                    result.append('\n')
                elif next_char == 'r':
                    result.append('\r')
                elif next_char == 't':
                    result.append('\t')
                else:
                    raise ValueError(f"Invalid escape sequence '\\{next_char}'")
            else:
                result.append(char)
            
            self.pos += 1
        
        if self.pos >= len(self.text):
            raise ValueError("Unterminated string")
        
        self.pos += 1  # Skip closing quote
        return ''.join(result)
    
    def _decode_number(self) -> float:
        """Decode number."""
        start = self.pos
        
        if self.text[self.pos] == '-':
            self.pos += 1
        
        if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
            raise ValueError("Invalid number")
        
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ValueError("Invalid number")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        num_str = self.text[start:self.pos]
        if '.' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    
    def _decode_dict(self) -> Dict:
        """Decode dictionary."""
        if self.text[self.pos] != '{':
            raise ValueError("Expected '{'")
        
        self.pos += 1
        result = {}
        
        self._skip_whitespace()
        
        # Empty dict
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return result
        
        while True:
            self._skip_whitespace()
            
            # Decode key (must be string)
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise ValueError("Expected string key in dict")
            
            key = self._decode_string()
            
            # Expect colon
            self._skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise ValueError("Expected ':' after key in dict")
            self.pos += 1
            
            # Decode value
            value = self._decode_value()
            result[key] = value
            
            # Check for comma or end
            self._skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("Unexpected end of dict")
            
            if self.text[self.pos] == '}':
                self.pos += 1
                break
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise ValueError(f"Expected ',' or '}}' in dict, got '{self.text[self.pos]}'")
        
        return result
    
    def _decode_list(self) -> List:
        """Decode list."""
        if self.text[self.pos] != '[':
            raise ValueError("Expected '['")
        
        self.pos += 1
        result = []
        
        self._skip_whitespace()
        
        # Empty list
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return result
        
        while True:
            value = self._decode_value()
            result.append(value)
            
            self._skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("Unexpected end of list")
            
            if self.text[self.pos] == ']':
                self.pos += 1
                break
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise ValueError(f"Expected ',' or ']' in list, got '{self.text[self.pos]}'")
        
        return result
    
    def _decode_true(self) -> bool:
        """Decode true literal."""
        if self.text[self.pos:self.pos+4] == 'true':
            self.pos += 4
            return True
        raise ValueError("Invalid literal")
    
    def _decode_false(self) -> bool:
        """Decode false literal."""
        if self.text[self.pos:self.pos+5] == 'false':
            self.pos += 5
            return False
        raise ValueError("Invalid literal")
    
    def _decode_null(self) -> None:
        """Decode null literal."""
        if self.text[self.pos:self.pos+4] == 'null':
            self.pos += 4
            return None
        raise ValueError("Invalid literal")
    
    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1


def json_dumps(obj: Any, indent: int = None) -> str:
    """Serialize object to JSON string."""
    json_str = JSONEncoder.encode(obj)
    
    if indent:
        return _format_json(json_str, indent)
    return json_str


def json_loads(s: str) -> Any:
    """Deserialize JSON string to object."""
    decoder = JSONDecoder(s)
    return decoder.decode()


def _format_json(json_str: str, indent: int) -> str:
    """Format JSON string with indentation."""
    result = []
    level = 0
    i = 0
    in_string = False
    
    while i < len(json_str):
        char = json_str[i]
        
        # Handle string escaping
        if char == '"' and (i == 0 or json_str[i-1] != '\\'):
            in_string = not in_string
        
        if not in_string:
            if char in '{[':
                result.append(char)
                level += 1
                result.append('\n' + ' ' * (level * indent))
            elif char in '}]':
                level -= 1
                result.append('\n' + ' ' * (level * indent))
                result.append(char)
            elif char == ',':
                result.append(char)
                result.append('\n' + ' ' * (level * indent))
            elif char == ':':
                result.append(': ')
            elif char == ' ':
                # Skip spaces outside strings (we'll add our own)
                i += 1
                continue
            else:
                result.append(char)
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)
