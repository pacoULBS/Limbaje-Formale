# Diferențe între LRParser2.py și tema4.py

## Rezumat
`tema4.py` extinde `LRParser2.py` cu funcționalitate de **Push Down Translator** - evaluează expresii și generează cod intermediar.

## Diferențe principale

### 1. STIVA DE ATRIBUTE (NOU în tema4.py)

**LRParser2.py** - doar 2 stive:
```python
state_stack = [0]
token_stack = ['$']
```

**tema4.py** - adaugă a 3-a stivă:
```python
state_stack = [0]
token_stack = ['$']
attribute_stack = [None]  # ← NOUĂ! Pentru valori semantice
```

### 2. OPERAȚIA SHIFT

**LRParser2.py**:
```python
if action.startswith('d'):
    next_state = int(action[1:])
    state_stack.append(next_state)
    token_stack.append(current_token)  # doar token
    pointer += 1
```

**tema4.py** - adaugă valoare semantică:
```python
if action.startswith('d'):
    next_state = int(action[1:])
    state_stack.append(next_state)
    token_stack.append(current_token)
    
    # ← NOU! Push valoare semantică
    if current_token == 'id':
        value = get_id_value(current_token)
        attribute_stack.append(value)
    else:
        attribute_stack.append(current_token)
    
    pointer += 1
```

### 3. OPERAȚIA REDUCE

**LRParser2.py** - doar validare sintactică:
```python
elif action.startswith('r'):
    # ... pop din state_stack și token_stack
    for i in range(rhs_length):
        state_stack.pop()
        x = token_stack.pop()
    
    token_stack.append(lhs)  # push simbol
    # ... goto
```

**tema4.py** - adaugă calcul semantic:
```python
elif action.startswith('r'):
    # ... pop și colectează atribute
    reduced_attributes = []
    for i in range(rhs_length):
        state_stack.pop()
        token = token_stack.pop()
        attr = attribute_stack.pop()  # ← NOU!
        reduced_attributes.append((token, attr))
    
    # ← NOU! ACȚIUNI SEMANTICE
    if prod_number == '2':  # E -> E + T
        e_val = reduced_attributes[0][1]
        t_val = reduced_attributes[2][1]
        result_value = e_val + t_val  # ← CALCULEAZĂ
        temp = new_temp()
        intermediate_code.append(f"{temp} = {e_val} + {t_val}")  # ← COD
    
    elif prod_number == '4':  # T -> T * F
        t_val = reduced_attributes[0][1]
        f_val = reduced_attributes[2][1]
        result_value = t_val * f_val  # ← CALCULEAZĂ
        temp = new_temp()
        intermediate_code.append(f"{temp} = {t_val} * {f_val}")  # ← COD
    
    # ... alte producții
    
    token_stack.append(lhs)
    attribute_stack.append(result_value)  # ← NOU! Push rezultat
    # ... goto
```

### 4. RETURNARE REZULTAT

**LRParser2.py**:
```python
elif action in ('acc', 'accept'):
    print("Input accepted.")
    return True  # doar validare
```

**tema4.py**:
```python
elif action in ('acc', 'accept'):
    print("Input accepted!")
    final_result = attribute_stack[...]  # ← NOU! Extrage rezultat
    print(f"Final result: {final_result}")
    return True, final_result, intermediate_code  # ← NOU!
```

### 5. FUNCȚII NOI ADĂUGATE

În **tema4.py**:
```python
def get_id_value(token):
    """Simulează valori pentru identificatori"""
    # Returnează 1, 2, 3, ... pentru fiecare id

def new_temp():
    """Generează variabile temporare t1, t2, ..."""
    # Pentru cod intermediar

def parse_and_evaluate(input_string):
    """Parser + evaluare - returnează (success, result, code)"""
    # Funcție principală nouă

# Funcții de test
def test_evaluation()
def test_simple()
def test_parentheses()
def test_invalid()
def run_all_tests()
```

## Tabel comparativ

| Caracteristică | LRParser2.py | tema4.py |
|----------------|--------------|----------|
| **Scop** | Validare sintaxă | Evaluare + cod intermediar |
| **Stive** | 2 (state, token) | 3 (state, token, attribute) |
| **Returnează** | bool (accept/reject) | (bool, result, code) |
| **Shift** | Push token | Push token + valoare |
| **Reduce** | Pop și push simbol | Pop, calculează, push rezultat |
| **Cod intermediar** | Nu | Da (t1 = 2 * 3, etc.) |
| **Teste automate** | 2 funcții | 5 funcții (suite completă) |
| **Mod interactiv** | Da | Da (îmbunătățit) |
| **CLI arguments** | Nu | Da (--test, expresii) |

## Exemplu vizual

### Input: `id + id * id`

**LRParser2.py** output:
```
Shift: Move to state 2, consume 'id'
Reduce: Using production 7: F -> id
...
Input accepted.
→ True
```

**tema4.py** output:
```
Shift: Move to state 2, consume 'id' with value 1
Reduce: Using production 7: F -> id
  Semantic action: F.val = id.val = 1
...
Reduce: Using production 4: T -> T * F
  Semantic action: T.val = 2 * 3 = 6
  Intermediate code: t1 = 2 * 3
Reduce: Using production 2: E -> E + T
  Semantic action: E.val = 1 + 6 = 7
  Intermediate code: t2 = 1 + 6
...
Input accepted!
Final result: 7
→ (True, 7, ['t1 = 2 * 3', 't2 = 1 + 6'])
```

## Concluzie

`tema4.py` = `LRParser2.py` + **Push Down Translator features**:
- ✅ Attribute stack
- ✅ Semantic actions
- ✅ Expression evaluation
- ✅ Intermediate code generation
- ✅ Complete test suite
