from parser import Parser, TokenType
from scanner import Token

def read_tokens_from_file(filename):

    tokens = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<') and line.endswith('>'):
                line = line[1:-1]  #Remove the surrounding <>
                if ', ' in line:
                    token_type, token_value = line.split(', ', 1)
                else:
                    token_type = line
                    token_value = None
                token_type = token_type.strip()
                if token_value:
                    token_value = token_value.strip()

                tokens.append(Token(token_type, token_value))


    return tokens

def main():
    
    tokens = read_tokens_from_file('input1.txt')

    class TestLexer:
        def __init__(self, tokens):
            self.tokens = tokens
            self.index = 0

        def get_next_token(self):
            if self.index < len(self.tokens):
                token = self.tokens[self.index]
                self.index += 1
                return token
            else:
                return Token(TokenType.EOF, 'EOF')

    lexer = TestLexer(tokens)
    parser = Parser(lexer)

    #Print to the output file
    try:
        parse_tree = parser.parse()
        with open('output.txt', 'w') as output_file:
            print("Parse Tree:", file=output_file)
            parse_tree.print_tree(file=output_file)
    except Exception as e:
        with open('output.txt', 'w') as output_file:
            print(f"Syntax Error: {e}", file=output_file)


if __name__ == "__main__":
    main()
