# parser.py
from scanner import Lexer, TokenType

class Node:
    def __init__(self, label=None, value=None, is_leaf=False):
        self.label = label
        self.value = value
        self.children = []
        self.is_leaf = is_leaf

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, depth=0, file=None):
        indent = " " * depth
        if self.is_leaf:
            if self.value:
                print(f"{indent}{self.label}: {self.value}", file=file)
            else:
                print(f"{indent}{self.label}", file=file)
        else:
            print(f"{indent}{self.label}", file=file)
            for child in self.children:
                child.print_tree(depth + 2, file=file)

    @staticmethod
    def create_leaf(label, value=None):
        return Node(label=label, value=value, is_leaf=True)



class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def get_next_token(self):
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        #Consumes a token if it matches the expected type
        if self.current_token.type == token_type:
            self.get_next_token()
        else:
            raise Exception(f"Expected token {token_type}, got {self.current_token.type}")

    def parse(self):
        #Starts the parsing process, expecting either a value or a dictionary format
        self.get_next_token()

        root = Node("root")

        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.STRING:
                value_node = Node("value")
                value_node.add_child(Node.create_leaf("STRING", self.current_token.value))
                self.eat(TokenType.STRING)

                if self.current_token.type == TokenType.COLON:
                    value_node.add_child(Node.create_leaf(":"))
                    self.eat(TokenType.COLON)
                    # Parse the next token as the value after the label
                    value_node.add_child(self.value())
                else:
                    raise Exception("Expected COLON after STRING label in parse")

                root.add_child(value_node)
            else:
                root.add_child(self.value())

        return root

    def value(self):
        #Parses the value rule to match the grammar
        node = Node("value")

        if self.current_token.type == TokenType.LBRACKET:
            node.add_child(self.list())
        elif self.current_token.type == TokenType.LBRACE:
            node.add_child(self.dict())
        elif self.current_token.type == TokenType.STRING:
            node.add_child(Node.create_leaf("STRING", self.current_token.value))
            self.eat(TokenType.STRING)
        elif self.current_token.type == TokenType.NUMBER:
            #Semantic rule for invalid decimal numbers
            if '.' in str(self.current_token.value):
                parts = str(self.current_token.value).split('.')
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    raise Exception(f"Error type 1 at {self.current_token.value}: Invalid Decimal Numbers.")
            #Semantic rule for invalid numbers
            if str(self.current_token.value).startswith('0') and len(str(self.current_token.value)) > 1 and \
                    str(self.current_token.value)[1].isdigit():
                raise Exception(f"Error type 3 at {self.current_token.value}: Invalid Numbers.")
            if str(self.current_token.value).startswith('+') and not (
                    'e' in str(self.current_token.value).lower()):
                raise Exception(f"Error type 3 at {self.current_token.value}: Invalid Numbers.")
            node.add_child(Node.create_leaf("NUMBER", self.current_token.value))
            self.eat(TokenType.NUMBER)
        elif self.current_token.type == TokenType.TRUE:
            node.add_child(Node.create_leaf("BOOL", "true"))
            self.eat(TokenType.TRUE)
        elif self.current_token.type == TokenType.FALSE:
            node.add_child(Node.create_leaf("BOOL", "false"))
            self.eat(TokenType.FALSE)
        elif self.current_token.type == TokenType.NULL:
            node.add_child(Node.create_leaf("NULL", "null"))
            self.eat(TokenType.NULL)
        else:
            raise Exception(f"Unexpected token {self.current_token.type} in value")

        return node

    def list(self):
        #Parses the list rule, ensuring all elements are of the same type
        list_node = Node("list")

        # Add opening bracket
        self.eat(TokenType.LBRACKET)
        list_node.add_child(Node.create_leaf("["))

        # Parse the first value in the list
        first_value = self.value()
        list_node.add_child(first_value)
        first_type = first_value.children[0].label

        #Parse additional values, if any, separated by commas
        while self.current_token.type == TokenType.COMMA:
            # Add comma node
            list_node.add_child(Node.create_leaf(","))
            self.eat(TokenType.COMMA)

            #Add subsequent value nodes
            next_value = self.value()
            next_type = next_value.children[0].label

            #Check if the type matches the first element's type
            if next_type != first_type:
                raise Exception(f"Error type 6 at : List elements must be of the same type. Expected {first_type}, got {next_type}")

            list_node.add_child(next_value)

        #Add closing bracket
        list_node.add_child(Node.create_leaf("]"))
        self.eat(TokenType.RBRACKET)

        return list_node

    def dict(self):
        #Parses the dict rule, ensuring all values are of the same type
        dict_node = Node("dict")
        keys = set()

        # Add opening brace
        dict_node.add_child(Node.create_leaf("{"))
        self.eat(TokenType.LBRACE)

        # Parse the first pair in the dictionary
        if self.current_token.type == TokenType.STRING:
            first_pair = self.pair()
            key = first_pair.children[0].value
            if key in keys:
                raise Exception(f'Error type 5 at "{key}": No Duplicate Keys in Dictionary')
            keys.add(key)
            dict_node.add_child(first_pair)
            first_value_type = first_pair.children[2].label

        # Parse additional pairs, if any, separated by commas
        while self.current_token.type == TokenType.COMMA:
            dict_node.add_child(Node.create_leaf(","))
            self.eat(TokenType.COMMA)
            next_pair = self.pair()
            key = next_pair.children[0].value
            if key in keys:
                raise Exception(f'Error type 5 at "{key}": No Duplicate Keys in Dictionary')
            keys.add(key)
            next_value_type = next_pair.children[2].label

            # Check if the value type matches the first pair's value type
            if next_value_type != first_value_type:
                raise Exception(
                    f"Dictionary values must be of the same type. Expected {first_value_type}, got {next_value_type}")

            dict_node.add_child(next_pair)

        # Add closing brace
        dict_node.add_child(Node.create_leaf("}"))
        self.eat(TokenType.RBRACE)

        return dict_node

    def pair(self):
        #Parses the pair rule
        pair_node = Node("pair")

        # Add key
        if self.current_token.type == TokenType.STRING:
            # Semantic rule for empty key
            if self.current_token.value.strip() == "":
                raise Exception(f'Error type 2 at "{self.current_token.value}": Empty Key')
            # Semantic rule for reserved words as dictionary key
            if self.current_token.value in ["true", "false"]:
                raise Exception(f'Error type 4 at "{self.current_token.value}": Reserved Words as Dictionary Key')
            pair_node.add_child(Node.create_leaf("STRING", self.current_token.value))
            self.eat(TokenType.STRING)
        else:
            raise Exception(f"Expected STRING as key in pair, got {self.current_token.type}")

        # Add colon
        if self.current_token.type == TokenType.COLON:
            pair_node.add_child(Node.create_leaf(":"))
            self.eat(TokenType.COLON)
        else:
            raise Exception(f"Expected COLON in pair, got {self.current_token.type}")

        # Add value
        value_node = self.value()
        if value_node.children[0].label not in ["STRING", "NUMBER"]:
            raise Exception(f"Expected STRING or NUMBER as value in pair, got {value_node.children[0].label}")
        pair_node.add_child(value_node)

        return pair_node
