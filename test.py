from xml.lexer import Lexer

with open('test.html', 'rb') as f:
    data = f.read()
    lex  = Lexer(data)
    while True:
        token = lex.next()
        if token is None:
            break
        print(token)
