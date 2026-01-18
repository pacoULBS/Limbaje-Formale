import csv

"""
tema4.py - Push Down Translator pentru expresii aritmetice

Acest program extinde LRParser2.py cu capacitatea de a evalua expresii aritmetice
și de a genera cod intermediar. Adaugă o stivă de atribute (attribute stack) pentru
a păstra valorile semantice în timpul parsării.

Diferența față de LRParser2.py:
- Stiva de atribute pentru valori semantice
- Acțiuni semantice în timpul reducerii
- Returnează rezultatul calculat, nu doar acceptare/respingere
"""

def read_action_table():
    """Citește tabela de acțiuni din action_table.csv"""
    action_table = {}
    with open('action_table.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            symbol = row[0]  # simbol (id, +, etc.)
            values = row[1:]  # restul valorilor din rand
            action_table[symbol] = values
    return action_table

def read_prod():
    """Citește producțiile din result.csv"""
    prod = {}
    with open('result.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            symbol = row[0]
            values = row[1:]
            prod[symbol] = values
    return prod

action_table = read_action_table()
print("Action Table:")
for key, values in action_table.items():
    print(f"{key}: {','.join(values)}")

prod = read_prod()
print("\nProductions:")
for key, values in prod.items():
    print(f"{key}: {','.join(values)}")

# ============================================================================
# PUSH DOWN TRANSLATOR - Adăugiri noi față de LRParser2.py
# ============================================================================

def parse_and_evaluate(input_string):
    """
    Parser LR cu stivă de atribute pentru evaluarea expresiilor aritmetice.
    
    Adăugiri față de LRParser2.py:
    - attribute_stack: stivă pentru valorile semantice
    - Acțiuni semantice în timpul reducerii
    - Returnează valoarea calculată
    
    Args:
        input_string: expresie aritmetică (ex: "id + id * id")
    
    Returns:
        Tuple (success: bool, result: int/None, intermediate_code: list)
    """
    state_stack = [0]  # stiva de stari cu 0
    token_stack = ['$']  # stiva de tokeni cu simbolul de start
    
    # ===== NOUĂ STIVĂ DE ATRIBUTE =====
    # Păstrează valori semantice (numere) pentru fiecare simbol din token_stack
    attribute_stack = [None]  # corespunde cu '$'
    
    # Pentru generarea de cod intermediar
    intermediate_code = []
    temp_counter = [0]  # counter pentru variabile temporare
    
    # Procesăm input-ul
    input_tokens = input_string.split() + ['$']
    pointer = 0
    
    # Pentru a simula valori pentru 'id', le înlocuim cu numere
    # În practică, valorile ar veni dintr-o tabelă de simboluri
    id_values = {}
    id_counter = [1]
    
    def get_id_value(token):
        """Returnează o valoare pentru un identificator"""
        if token == 'id':
            # Simulăm că fiecare 'id' are valoarea 1, 2, 3, etc.
            val = id_counter[0]
            id_counter[0] += 1
            return val
        return None
    
    def new_temp():
        """Generează o nouă variabilă temporară"""
        temp_counter[0] += 1
        return f"t{temp_counter[0]}"
    
    while True:
        current_state = state_stack[-1]
        current_token = input_tokens[pointer]
        
        try:
            action = action_table.get(current_token, [])[current_state]
        except IndexError:
            print("Input rejected: Invalid state or token.")
            return False, None, intermediate_code
        
        # ===== ACȚIUNE DE DEPLASARE (SHIFT) =====
        if action.startswith('d'):
            next_state = int(action[1:])
            state_stack.append(next_state)
            token_stack.append(current_token)
            
            # ===== PUSH LA STIVA DE ATRIBUTE =====
            # Dacă e 'id', punem valoarea lui; altfel, punem operatorul
            if current_token == 'id':
                value = get_id_value(current_token)
                attribute_stack.append(value)
                print(f"Shift: Move to state {next_state}, consume '{current_token}' with value {value}")
            else:
                attribute_stack.append(current_token)
                print(f"Shift: Move to state {next_state}, consume '{current_token}'")
            
            pointer += 1
            
        # ===== ACȚIUNE DE REDUCERE (REDUCE) =====
        elif action.startswith('r'):
            prod_number = action[1:]
            entry = prod.get(prod_number)
            if not entry:
                print(f"Input rejected: Unknown production {prod_number}.")
                return False, None, intermediate_code
            
            lhs = entry[0]  # partea stanga
            rhs = entry[1].strip() if len(entry) > 1 else ''  # partea dreapta
            rhs_tokens = rhs.split() if rhs else []
            rhs_length = len(rhs_tokens)
            
            # Colectăm atributele pentru evaluare
            reduced_attributes = []
            for i in range(rhs_length):
                state_stack.pop()
                token = token_stack.pop()
                attr = attribute_stack.pop()
                reduced_attributes.append((token, attr))
            
            # Inversăm pentru a obține ordinea corectă (left-to-right)
            reduced_attributes.reverse()
            
            # ===== ACȚIUNI SEMANTICE (EVALUARE) =====
            result_value = None
            
            # Producție 1: S -> E
            if prod_number == '1':
                # S moștenește valoarea lui E
                result_value = reduced_attributes[0][1] if reduced_attributes else None
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: S.val = E.val = {result_value}")
            
            # Producție 2: E -> E + T
            elif prod_number == '2':
                e_val = reduced_attributes[0][1]
                t_val = reduced_attributes[2][1]
                result_value = e_val + t_val
                temp = new_temp()
                intermediate_code.append(f"{temp} = {e_val} + {t_val}")
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: E.val = E.val + T.val = {e_val} + {t_val} = {result_value}")
                print(f"  Intermediate code: {temp} = {e_val} + {t_val}")
            
            # Producție 3: E -> T
            elif prod_number == '3':
                result_value = reduced_attributes[0][1]
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: E.val = T.val = {result_value}")
            
            # Producție 4: T -> T * F
            elif prod_number == '4':
                t_val = reduced_attributes[0][1]
                f_val = reduced_attributes[2][1]
                result_value = t_val * f_val
                temp = new_temp()
                intermediate_code.append(f"{temp} = {t_val} * {f_val}")
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: T.val = T.val * F.val = {t_val} * {f_val} = {result_value}")
                print(f"  Intermediate code: {temp} = {t_val} * {f_val}")
            
            # Producție 5: T -> F
            elif prod_number == '5':
                result_value = reduced_attributes[0][1]
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: T.val = F.val = {result_value}")
            
            # Producție 6: F -> ( E )
            elif prod_number == '6':
                e_val = reduced_attributes[1][1]
                result_value = e_val
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: F.val = E.val = {result_value}")
            
            # Producție 7: F -> id
            elif prod_number == '7':
                result_value = reduced_attributes[0][1]
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: F.val = id.val = {result_value}")
            
            else:
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                result_value = None
            
            # Adăugăm simbolul redus pe stiva
            token_stack.append(lhs)
            attribute_stack.append(result_value)
            
            # GOTO
            try:
                goto_cell = action_table.get(lhs, [])[state_stack[-1]]
                goto_state = int(goto_cell)
            except (IndexError, ValueError):
                print("Input rejected: Invalid goto for reduction.")
                return False, None, intermediate_code
            
            state_stack.append(goto_state)
            print(f"  Goto state {goto_state}")
        
        # ===== ACCEPTARE =====
        elif action in ('acc', 'accept'):
            print("\n" + "="*60)
            print("Input accepted!")
            # Rezultatul final este pe stiva de atribute
            # După ultima reducere la S, avem pe stivă: [None (pentru $), result_value (pentru S)]
            # Extragem valoarea pentru S care este penultimul element
            final_result = None
            for i in range(len(token_stack) - 1, -1, -1):
                if token_stack[i] == 'S':
                    final_result = attribute_stack[i]
                    break
            print(f"Final result: {final_result}")
            print("="*60)
            return True, final_result, intermediate_code
        
        else:
            print("Input rejected.")
            return False, None, intermediate_code


# ============================================================================
# FUNCȚII DE TEST
# ============================================================================

def test_evaluation():
    """Test pentru evaluarea expresiilor"""
    print("\n" + "="*60)
    print("TEST 1: Evaluarea expresiei 'id + id * id'")
    print("="*60)
    success, result, code = parse_and_evaluate("id + id * id")
    
    if success:
        print(f"\n✓ Test passed: Result = {result}")
        print(f"✓ Intermediate code:")
        for line in code:
            print(f"  {line}")
        assert result == 1 + 2 * 3  # id1=1, id2=2, id3=3
        return True
    else:
        print("\n✗ Test failed")
        return False

def test_simple():
    """Test pentru expresie simplă"""
    print("\n" + "="*60)
    print("TEST 2: Evaluarea expresiei 'id * id + id'")
    print("="*60)
    success, result, code = parse_and_evaluate("id * id + id")
    
    if success:
        print(f"\n✓ Test passed: Result = {result}")
        print(f"✓ Intermediate code:")
        for line in code:
            print(f"  {line}")
        assert result == 1 * 2 + 3  # id1=1, id2=2, id3=3
        return True
    else:
        print("\n✗ Test failed")
        return False

def test_parentheses():
    """Test pentru paranteze"""
    print("\n" + "="*60)
    print("TEST 3: Evaluarea expresiei '( id + id ) * id'")
    print("="*60)
    success, result, code = parse_and_evaluate("( id + id ) * id")
    
    if success:
        print(f"\n✓ Test passed: Result = {result}")
        print(f"✓ Intermediate code:")
        for line in code:
            print(f"  {line}")
        assert result == (1 + 2) * 3  # (id1 + id2) * id3
        return True
    else:
        print("\n✗ Test failed")
        return False

def test_invalid():
    """Test pentru șir invalid"""
    print("\n" + "="*60)
    print("TEST 4: Testarea șirului invalid 'id * * + id'")
    print("="*60)
    success, result, code = parse_and_evaluate("id * * + id")
    
    if not success:
        print("\n✓ Test passed: Invalid input correctly rejected")
        return True
    else:
        print("\n✗ Test failed: Should have rejected invalid input")
        return False

def run_all_tests():
    """Rulează toate testele"""
    print("\n" + "="*70)
    print(" PUSH DOWN TRANSLATOR - Test Suite")
    print("="*70)
    
    tests = [test_evaluation, test_simple, test_parentheses, test_invalid]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*70)
    print(f" RESULTS: {passed}/{len(tests)} tests passed")
    print("="*70)
    
    return passed == len(tests)


# ============================================================================
# MAIN - Poate fi folosit interactiv sau pentru teste
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Verificăm dacă avem argumente
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Rulăm testele
            run_all_tests()
        else:
            # Parsăm expresia dată ca argument
            expr = " ".join(sys.argv[1:])
            print(f"\nEvaluating expression: {expr}")
            success, result, code = parse_and_evaluate(expr)
            if success:
                print(f"\nFinal result: {result}")
                if code:
                    print("\nIntermediate code:")
                    for line in code:
                        print(f"  {line}")
    else:
        # Mod interactiv
        print("\n" + "="*70)
        print(" PUSH DOWN TRANSLATOR - Interactive Mode")
        print("="*70)
        print("\nOptions:")
        print("  1. Enter 'test' to run test suite")
        print("  2. Enter an arithmetic expression (e.g., 'id + id * id')")
        print("  3. Enter 'exit' to quit")
        print("="*70)
        
        while True:
            try:
                user_input = input("\nEnter expression (or 'test'/'exit'): ").strip()
                
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'test':
                    run_all_tests()
                elif user_input:
                    success, result, code = parse_and_evaluate(user_input)
                    if success and result is not None:
                        print(f"\n{'='*40}")
                        print(f"Final result: {result}")
                        if code:
                            print("\nIntermediate code:")
                            for line in code:
                                print(f"  {line}")
                        print(f"{'='*40}")
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                break
