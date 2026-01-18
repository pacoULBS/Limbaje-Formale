# Tema 4 - Push Down Translator pentru Expresii Aritmetice

## Descriere

`tema4.py` este un **Push Down Translator** pentru expresii aritmetice care extinde funcționalitatea din `LRParser2.py`. În loc să valideze doar sintaxa, acest translator evaluează expresiile și generează cod intermediar.

## Diferențe față de LRParser2.py

### Cod original (LRParser2.py)
- Validează doar sintaxa expresiilor
- Returnează doar `True`/`False` (acceptat/respins)
- Folosește doar stive pentru stări și tokeni

### Cod nou (tema4.py)
- **Stivă de atribute nouă**: păstrează valorile semantice pentru fiecare simbol
- **Acțiuni semantice**: calculează rezultate în timpul reducerii
- **Generare de cod intermediar**: produce instrucțiuni de tip trei-adrese
- **Returnează rezultatul calculat**: evaluează expresia arithmetic

## Componente noi

### 1. Stiva de atribute (Attribute Stack)
```python
attribute_stack = [None]  # sincronizată cu token_stack
```

Păstrează:
- Valori numerice pentru identificatori (`id`)
- Operatori (`+`, `*`, `(`, `)`)
- Rezultate intermediare calculate

### 2. Acțiuni semantice pentru fiecare producție

| Producție | Acțiune semantică |
|-----------|-------------------|
| S → E | S.val = E.val |
| E → E + T | E.val = E.val + T.val; generează `t = E.val + T.val` |
| E → T | E.val = T.val |
| T → T * F | T.val = T.val * F.val; generează `t = T.val * F.val` |
| T → F | T.val = F.val |
| F → ( E ) | F.val = E.val |
| F → id | F.val = id.val |

### 3. Generare cod intermediar

Produce instrucțiuni de forma:
```
t1 = 2 * 3
t2 = 1 + 6
```

## Utilizare

### 1. Mod test (automat)
```bash
python3 tema4.py --test
```

Rulează 4 teste:
- `id + id * id` → rezultat: 7
- `id * id + id` → rezultat: 5
- `( id + id ) * id` → rezultat: 9
- `id * * + id` → invalid (respins corect)

### 2. Mod cu argument
```bash
python3 tema4.py "id + id * id"
```

### 3. Mod interactiv
```bash
python3 tema4.py
```

Apoi introduceți expresii sau:
- `test` - rulează testele
- `exit` - ieșire

## Exemplu de execuție

```bash
$ python3 tema4.py "id + id * id"

Evaluating expression: id + id * id
Shift: Move to state 2, consume 'id' with value 1
Reduce: Using production 7: F -> id
  Semantic action: F.val = id.val = 1
...
Reduce: Using production 4: T -> T * F
  Semantic action: T.val = T.val * F.val = 2 * 3 = 6
  Intermediate code: t1 = 2 * 3
...
Reduce: Using production 2: E -> E + T
  Semantic action: E.val = E.val + T.val = 1 + 6 = 7
  Intermediate code: t2 = 1 + 6
...

============================================================
Input accepted!
Final result: 7
============================================================

Final result: 7

Intermediate code:
  t1 = 2 * 3
  t2 = 1 + 6
```

## Arhitectură tehnică

### Algoritmul Push Down Translator

1. **Inițializare**:
   - state_stack = [0]
   - token_stack = ['$']
   - attribute_stack = [None]

2. **Pentru fiecare token**:
   
   **SHIFT (deplasare)**:
   - Push stare, token și valoare semantică pe stive
   - Pentru `id`: atribuie valoare numerică (1, 2, 3, ...)
   
   **REDUCE (reducere)**:
   - Pop simboluri conform producției
   - Aplică acțiune semantică:
     - Pentru operații: calculează rezultat
     - Pentru paranteze: propagă valoare
   - Generează cod intermediar (dacă e operație)
   - Push rezultat pe attribute_stack
   
   **ACCEPT**:
   - Extrage rezultatul final din attribute_stack

### Simulare valori pentru identificatori

În absența unei tabele de simboluri reale, programul atribuie secvențial:
- primul `id` → valoarea 1
- al doilea `id` → valoarea 2
- al treilea `id` → valoarea 3
- etc.

Acest lucru permite testarea funcționalității fără input complex.

## Fișiere necesare

- `tema4.py` - translator principal
- `action_table.csv` - tabelă de acțiuni LR(1)
- `result.csv` - producții numerotate

Aceste tabele sunt generate de `tema3.py` pentru gramatica:
```
S → E
E → E + T | T
T → T * F | F
F → ( E ) | id
```

## Teste

### Test 1: id + id * id
- Input: `id + id * id`
- Așteptat: 1 + 2 * 3 = 7
- Cod intermediar:
  ```
  t1 = 2 * 3
  t2 = 1 + 6
  ```

### Test 2: id * id + id
- Input: `id * id + id`
- Așteptat: 1 * 2 + 3 = 5
- Cod intermediar:
  ```
  t1 = 1 * 2
  t2 = 2 + 3
  ```

### Test 3: ( id + id ) * id
- Input: `( id + id ) * id`
- Așteptat: (1 + 2) * 3 = 9
- Cod intermediar:
  ```
  t1 = 1 + 2
  t2 = 3 * 3
  ```

### Test 4: id * * + id (invalid)
- Input: `id * * + id`
- Așteptat: respins (sintaxă invalidă)
- Rezultat: ✓ Correct rejection

## Concepte implementate

1. **Syntax-Directed Translation** - traducere ghidată de sintaxă
2. **Attribute Grammar** - gramatică cu atribute (valori semantice)
3. **Intermediate Code Generation** - generare cod intermediar (forma trei-adrese)
4. **Semantic Actions** - acțiuni executate în timpul parsării
5. **Value Stack** - stivă separată pentru evaluare

## Autor

Implementat pentru cursul de Limbaje Formale și Tehnici de Compilare.
Bazat pe parser LR(1) din `LRParser2.py`.
