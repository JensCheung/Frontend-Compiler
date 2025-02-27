
class TokenType:
    COMMA = 'COMMA'
    COLON = 'COLON'
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    FALSE = 'FALSE'
    TRUE = 'TRUE'
    NULL = 'NULL'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    LBRACE = 'LBRACE'     #{
    RBRACE = 'RBRACE'     #}
    EOF = 'EOF'


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.type == TokenType.STRING:
            return f"<str, {self.value}>"
        elif self.type == TokenType.NUMBER:
            return f"<num, {self.value}>"
        elif self.type == TokenType.LBRACE:
            return "<{>"
        elif self.type == TokenType.RBRACE:
            return "<}>"
        elif self.type == TokenType.LBRACKET:
            return "<[>"
        elif self.type == TokenType.RBRACKET:
            return "<]> "
        elif self.type == TokenType.COMMA:
            return "<,>"
        elif self.type == TokenType.COLON:
            return "<:>"
        elif self.type == TokenType.FALSE:
            return "<FALSE>"
        elif self.type == TokenType.TRUE:
            return "<TRUE>"
        elif self.type == TokenType.NULL:
            return "<NULL>"
        else:
            return f"<{self.type}>"


class LexerError(Exception):
    def __init__(self, position, character):
        self.position = position
        self.character = character
        super().__init__(f"Invalid character '{character}' at position {position}")


class Lexer:
    def __init__(self, input_text):
        # Input string
        self.input_text = input_text
        # Current position
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None
        # Track the type of the last token to distinguish between negative numbers and subtraction
        self.previous_token_type = None

    # Input Buffering
    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            # End of input
            self.current_char = None
        else:
            self.current_char = self.input_text[self.position]

    # Skip whitespace
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Recognize strings
    def recognize_string(self):
        result = ''
        self.advance()  # Skip the opening quote
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # Skip the closing quote
        return Token(TokenType.STRING, result)

    # Recognize numbers
    def recognize_number(self):
        result = ''
        if self.current_char == '-':  # Handle negative numbers
            result += '-'
            self.advance()
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char in ['.', 'e', 'E']):
            result += self.current_char
            self.advance()
        return Token(TokenType.NUMBER, float(result))

    def recognize_true(self):
        result = ''
        for _ in range(4):  # 'true' has 4 characters
            if self.current_char is not None and self.current_char == 'true'[_]:
                result += self.current_char
                self.advance()
            else:
                raise LexerError(self.position, self.current_char)
        return Token(TokenType.TRUE, result)

    def recognize_false(self):
        result = ''
        for _ in range(5):  # 'false' has 5 characters
            if self.current_char is not None and self.current_char == 'false'[_]:
                result += self.current_char
                self.advance()
            else:
                raise LexerError(self.position, self.current_char)
        return Token(TokenType.FALSE, result)

    def recognize_null(self):
        result = ''
        for _ in range(4):  # 'null' has 4 characters
            if self.current_char is not None and self.current_char == 'null'[_]:
                result += self.current_char
                self.advance()
            else:
                raise LexerError(self.position, self.current_char)
        return Token(TokenType.NULL, result)

    # Get next token from input
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char == '{':
                self.advance()
                self.previous_token_type = TokenType.LBRACE
                return Token(TokenType.LBRACE, '{')
            if self.current_char == '}':
                self.advance()
                self.previous_token_type = TokenType.RBRACE
                return Token(TokenType.RBRACE, '}')
            if self.current_char == '[':
                self.advance()
                self.previous_token_type = TokenType.LBRACKET
                return Token(TokenType.LBRACKET, '[')
            if self.current_char == ']':
                self.advance()
                self.previous_token_type = TokenType.RBRACKET
                return Token(TokenType.RBRACKET, ']')
            if self.current_char == ',':
                self.advance()
                self.previous_token_type = TokenType.COMMA
                return Token(TokenType.COMMA, ',')
            if self.current_char == ':':
                self.advance()
                self.previous_token_type = TokenType.COLON
                return Token(TokenType.COLON, ':')
            if self.input_text[self.position:self.position + 4] == 'true':
                self.previous_token_type = TokenType.TRUE
                return self.recognize_true()
            if self.input_text[self.position:self.position + 5] == 'false':
                self.previous_token_type = TokenType.FALSE
                return self.recognize_false()
            if self.input_text[self.position:self.position + 4] == 'null':
                self.previous_token_type = TokenType.NULL
                return self.recognize_null()
            if self.current_char == '"':
                self.previous_token_type = TokenType.STRING
                return self.recognize_string()
            if self.current_char.isdigit() or self.current_char == '-':
                self.previous_token_type = TokenType.NUMBER
                return self.recognize_number()
            raise LexerError(self.position, self.current_char)

        return Token(TokenType.EOF, 'EOF')

    # Tokenize the input
    def tokenize(self):
        tokens = []
        while True:
            try:
                token = self.get_next_token()
            except LexerError as e:
                print(f"Lexical Error: {e}")
                break
            if token.type == TokenType.EOF:
                break
            tokens.append(token)
        return tokens



