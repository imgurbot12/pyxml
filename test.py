from xml.lexer import Lexer


def iterate(stream):
    for byte in stream:
        yield byte


with open('test.html', 'rb') as f:
    data = f.read()
    lex = Lexer(iterate(data))
    while True:
        token = lex.next()
        if token is None:
            break
        print(token)
