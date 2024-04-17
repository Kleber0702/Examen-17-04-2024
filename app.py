from flask import Flask, render_template, request
import ply.lex as lex

app = Flask(__name__)

class Lexer:
    tokens = [
        'DELIMITADOR',
        'OPERADOR',
        'PALABRA_RESERVADA',
        'ENTERO',
        'IDENTIFICADOR',
        'PUNTO',
        'COMILLAS',
        'PARENTESIS_ABRIR',
        'PARENTESIS_CERRAR',
        'LLAVE_ABRIR',
        'LLAVE_CERRAR',
        'DOS_PUNTOS',
        'DESCONOCIDO'
    ]

    t_ignore = ' \t'

    reserved = {
        'using': 'USING',
        'System': 'SYSTEM',
        'namespace': 'NAMESPACE',
        'class': 'CLASS',
        'static': 'STATIC',
        'void': 'VOID',
        'Main': 'MAIN',
        'string': 'STRING',
        'args': 'ARGS',
        'Console': 'CONSOLE',
        'WriteLine': 'WRITELINE',
        '!': 'EXCLAMATION'
    }

    tokens += reserved.values()
    contador_lineas = 1
    token_count = {}
    contador_parentesis = 0
    contador_llaves = 0
    contador_parentes = 0
    cantidad_menor = None
    cantidad_menor_1 = None
    cantidad_menor_2 = None

    @staticmethod
    def t_DELIMITADOR(t):
        r'[;]'
        return t
    
    @staticmethod
    def limpiar():
        Lexer.contador_lineas = 1
        Lexer.token_count = {}
        Lexer.contador_parentesis = 0
        Lexer.contador_llaves = 0
        Lexer.contador_parentes = 0
        Lexer.cantidad_menor = 0
        Lexer.cantidad_menor_1 = 0
        Lexer.cantidad_menor_2 = 0
        Lexer.tokens = []

    @staticmethod
    def t_OPERADOR(t):
        r'[-+*/=<>]'
        if t.value == '<':
            Lexer.contador_parentesis += 1
        elif t.value == '>':
            Lexer.contador_parentesis -= 1
        return t

    @staticmethod
    def t_ENTERO(t):
        r'-?\b\d+\b'
        return t

    @staticmethod
    def t_IDENTIFICADOR(t):
        r'\b[a-zA-Z]+\b'
        if t.value == 'suma':
            t.type = 'IDENTIFICADOR'
        elif t.value == 'HelloWorld':
            t.type = 'IDENTIFICADOR' 
        else:
            t.type = 'PALABRA_RESERVADA' if t.value in Lexer.reserved else 'DESCONOCIDO'
        Lexer.token_count.setdefault(t.type, 0)
        Lexer.token_count[t.type] += 1
        return t

    @staticmethod
    def t_PUNTO(t):
        r'\.'
        return t

    @staticmethod
    def t_PALABRA_RESERVADA(t):
        r'for|do|public|static|const|main|class|programa|read|printf|end|using|System|namespace|class|static|void|Main|string|args|Console|WriteLine|!'
        t.type = Lexer.reserved.get(t.value, 'PALABRA_RESERVADA')
        return t

    @staticmethod
    def t_COMILLAS(t):
        r'\"'
        return t

    @staticmethod
    def t_PARENTESIS_ABRIR(t):
        r'\('
        if t.value == '(':
            Lexer.contador_llaves += 1
        return t

    @staticmethod
    def t_PARENTESIS_CERRAR(t):
        r'\)'
        if t.value == ')':
            Lexer.contador_llaves += 1
        return t

    @staticmethod
    def t_LLAVE_ABRIR(t):
        r'\{'
        if t.value == '{':
            Lexer.contador_llaves += 1
        return t

    @staticmethod
    def t_LLAVE_CERRAR(t):
        r'\}'
        if t.value == '}':
            Lexer.contador_llaves += 1
        return t
    
    @staticmethod
    def t_DOS_PUNTOS(t):
        r'\:'
        return t

    @staticmethod
    def t_newline(t):
        r'\n+'
        Lexer.contador_lineas += t.value.count('\n')
        t.lexer.lineno += t.value.count('\n')

    @staticmethod
    def t_eof(t):
        t.lexer.lineno += t.value.count('\n')
        return None

    @staticmethod
    def t_error(t):
        print(f"Error léxico: Carácter inesperado '{t.value[0]}' en la línea {Lexer.contador_lineas}")
        t.lexer.skip(1)

    @staticmethod
    def build():
        return lex.lex(module=Lexer())

lexer = Lexer.build()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analizar', methods=['POST'])
def analizar():
    Lexer.limpiar()
    entrada_text = request.form['entrada']
    lexer.lineno = 1
    lexer.input(entrada_text)
    tokens = []
    errores = []

    for tok in lexer:
        if tok.type != 'UNKNOWN':
            tokens.append((tok.type, tok.value, tok.lineno))
        elif tok.type == 'UNKNOWN':
            errores.append((f"Error léxico: Token no reconocido '{tok.value}'", tok.lineno))

    if Lexer.contador_parentes % 2 != 0:
        errores.append((f"Error: Carácter faltante " + "( o )", 0))    

    if Lexer.contador_llaves % 2 != 0:
            errores.append((f"Error: Carácter faltante " + "{ o }", 0))
    
    for i, line in enumerate(entrada_text.split('\n'), start=1):
            if '("' in line and ';' not in line:
                errores.append((f"Error: ; faltante ", i))
    if not errores:  # Si no hay errores, agregar "sin errores" a la lista de errores
            errores.append(("Sin errores",0))

    return render_template('index.html', tokens=tokens, errores=errores)

if __name__ == '__main__':
    app.run(debug=True)
