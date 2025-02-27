# Frontend-Compiler
The Frontend part of a compiler including the scanner, parser and semantic analysis.<br>
<br>

### Scanner
Takes json input to create tokens that are used by the parser<br>

### Parser
Takes the tokens and create a parse tree. The indentation is based on the depth of the element<br> for example an array will have depth 1 and it's elements depth of 2

### Semantic analysis
The "rules" for the language, check mechanisms for syntax errors, values such as ".23" or opening bracket without a closing bracket.
