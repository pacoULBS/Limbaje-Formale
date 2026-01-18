import LRParser2  # reuse base tables and parsing data

# Reuse tables from LRParser2
action_table = LRParser2.action_table
prod = LRParser2.prod

# Optional: debug printouts (disabled by default)
DEBUG_MODE = False
if DEBUG_MODE:
    print("Action Table:")
    for key, values in action_table.items():
        print(f"{key}: {','.join(values)}")
    print("\nProductions:")
    for key, values in prod.items():
        print(f"{key}: {','.join(values)}")

# ============================================================================
# ADDITIONS OVER LRParser2: parse_and_evaluate with attribute stack + tests
# ============================================================================

def parse_and_evaluate(input_string):
    """
    Parser LR cu stivă de atribute pentru evaluarea expresiilor aritmetice.
    Returnează (success: bool, result: int/None, intermediate_code: list)
    """
    state_stack = [0]
    token_stack = ['$']
    attribute_stack = [None]  # corespunde '$'

    intermediate_code = []
    temp_counter = 0

    input_tokens = input_string.split() + ['$']
    pointer = 0
    id_counter = 1  # valori simulate pentru 'id'

    def get_id_value(token):
        nonlocal id_counter
        if token == 'id':
            val = id_counter
            id_counter += 1
            return val
        return None

    def new_temp():
        nonlocal temp_counter
        temp_counter += 1
        return f"t{temp_counter}"

    while True:
        current_state = state_stack[-1]
        current_token = input_tokens[pointer]

        try:
            action = action_table.get(current_token, [])[current_state]
        except IndexError:
            print("Input rejected: Invalid state or token.")
            return False, None, intermediate_code

        if action.startswith('d'):  # SHIFT
            next_state = int(action[1:])
            state_stack.append(next_state)
            token_stack.append(current_token)

            if current_token == 'id':
                value = get_id_value(current_token)
                attribute_stack.append(value)
                print(f"Shift: Move to state {next_state}, consume '{current_token}' with value {value}")
            else:
                attribute_stack.append(current_token)
                print(f"Shift: Move to state {next_state}, consume '{current_token}'")

            pointer += 1

        elif action.startswith('r'):  # REDUCE
            prod_number = action[1:]
            entry = prod.get(prod_number)
            if not entry:
                print(f"Input rejected: Unknown production {prod_number}.")
                return False, None, intermediate_code

            lhs = entry[0]
            rhs = entry[1].strip() if len(entry) > 1 else ''
            rhs_tokens = rhs.split() if rhs else []
            rhs_length = len(rhs_tokens)

            reduced_attributes = []
            for _ in range(rhs_length):
                state_stack.pop()
                token = token_stack.pop()
                attr = attribute_stack.pop()
                reduced_attributes.append((token, attr))

            reduced_attributes.reverse()
            result_value = None

            if prod_number == '1':  # S -> E
                result_value = reduced_attributes[0][1] if reduced_attributes else None
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: S.val = E.val = {result_value}")

            elif prod_number == '2':  # E -> E + T
                e_val = reduced_attributes[0][1]
                t_val = reduced_attributes[2][1]
                result_value = e_val + t_val
                temp = new_temp()
                intermediate_code.append(f"{temp} = {e_val} + {t_val}")
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: E.val = E.val + T.val = {e_val} + {t_val} = {result_value}")
                print(f"  Intermediate code: {temp} = {e_val} + {t_val}")

            elif prod_number == '3':  # E -> T
                result_value = reduced_attributes[0][1]
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: E.val = T.val = {result_value}")

            elif prod_number == '4':  # T -> T * F
                t_val = reduced_attributes[0][1]
                f_val = reduced_attributes[2][1]
                result_value = t_val * f_val
                temp = new_temp()
                intermediate_code.append(f"{temp} = {t_val} * {f_val}")
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: T.val = T.val * F.val = {t_val} * {f_val} = {result_value}")
                print(f"  Intermediate code: {temp} = {t_val} * {f_val}")

            elif prod_number == '5':  # T -> F
                result_value = reduced_attributes[0][1]
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: T.val = F.val = {result_value}")

            elif prod_number == '6':  # F -> ( E )
                e_val = reduced_attributes[1][1]
                result_value = e_val
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: F.val = E.val = {result_value}")

            elif prod_number == '7':  # F -> id
                result_value = reduced_attributes[0][1]
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                print(f"  Semantic action: F.val = id.val = {result_value}")

            else:
                print(f"Reduce: Using production {prod_number}: {lhs} -> {rhs}")
                result_value = None

            token_stack.append(lhs)
            attribute_stack.append(result_value)

            try:
                goto_cell = action_table.get(lhs, [])[state_stack[-1]]
                goto_state = int(goto_cell)
            except (IndexError, ValueError):
                print("Input rejected: Invalid goto for reduction.")
                return False, None, intermediate_code

            state_stack.append(goto_state)
            print(f"  Goto state {goto_state}")

        elif action in ('acc', 'accept'):
            print("\n" + "="*60)
            print("Input accepted!")
            final_result = attribute_stack[-1] if len(attribute_stack) >= 1 else None
            print(f"Final result: {final_result}")
            print("="*60)
            return True, final_result, intermediate_code

        else:
            print("Input rejected.")
            return False, None, intermediate_code


# -------------------------- TESTE (opționale) --------------------------

def test_evaluation():
    print("\n" + "="*60)
    print("TEST 1: Evaluarea expresiei 'id + id * id'")
    print("="*60)
    success, result, code = parse_and_evaluate("id + id * id")
    if success:
        print(f"\n✓ Test passed: Result = {result}")
        print("✓ Intermediate code:")
        for line in code:
            print(f"  {line}")
        assert result == 1 + 2 * 3
        return True
    print("\n✗ Test failed")
    return False

def test_simple():
    print("\n" + "="*60)
    print("TEST 2: Evaluarea expresiei 'id * id + id'")
    print("="*60)
    success, result, code = parse_and_evaluate("id * id + id")
    if success:
        print(f"\n✓ Test passed: Result = {result}")
        print("✓ Intermediate code:")
        for line in code:
            print(f"  {line}")
        assert result == 1 * 2 + 3
        return True
    print("\n✗ Test failed")
    return False

def test_parentheses():
    print("\n" + "="*60)
    print("TEST 3: Evaluarea expresiei '( id + id ) * id'")
    print("="*60)
    success, result, code = parse_and_evaluate("( id + id ) * id")
    if success:
        print(f"\n✓ Test passed: Result = {result}")
        print("✓ Intermediate code:")
        for line in code:
            print(f"  {line}")
        assert result == (1 + 2) * 3
        return True
    print("\n✗ Test failed")
    return False

def test_invalid():
    print("\n" + "="*60)
    print("TEST 4: Testarea șirului invalid 'id * * + id'")
    print("="*60)
    success, result, code = parse_and_evaluate("id * * + id")
    if not success:
        print("\n✓ Test passed: Invalid input correctly rejected")
        return True
    print("\n✗ Test failed: Should have rejected invalid input")
    return False

def run_all_tests():
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_all_tests()
    else:
        expr = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Enter arithmetic expression (e.g., 'id + id * id'): ").strip()
        if expr:
            print(f"\nEvaluating expression: {expr}")
            success, result, code = parse_and_evaluate(expr)
            if success:
                print(f"\nFinal result: {result}")
                if code:
                    print("\nIntermediate code:")
                    for line in code:
                        print(f"  {line}")