import re
import ast


class Error_Checker:

    def __init__(self, filename):
        self.file = filename
        self.error_dict = {}

    def processing(self):

        count = 0
        line_counter = 1

        with open(self.file, 'r') as f:
            for line in f:
                cline = line.strip()

                self.check_len(cline, line_counter)
                self.check_indent(line, line_counter)
                self.check_semicolon(cline, line_counter)
                self.check_comment_spacing(line, line_counter)
                self.find_todo(cline, line_counter)

                count = self.check_blanklines(cline, count, line_counter)
                self.check_names(cline, line_counter)

                count += 1 if cline == '' else -count
                # print(cline, count, cline == '')

                line_counter += 1

        self.ast_checks()

    def check_len(self, x, line_count):
        if len(x) > 79:
            self.error_dict[str(line_count) + 'A'] = {'Code': 'S001', 'Message': 'Too Long'}

    def check_indent(self, x, line_count):
        count = 0

        for i in range(0, len(x)):
            if x[i] == " ":
                count += 1

            else:
                break

        if count % 4:
            self.error_dict[str(line_count) + 'B'] = \
                {'Code': 'S002', 'Message': 'Indentation is not a multiple of four'}

    def check_semicolon(self, x, line_count):
        index_a = x.find(";")
        index_b = x.find("#")
        index_c = x.find("'")
        index_c1 = x.find("'", index_c + 1)
        index_d = x.find("\"")
        index_d1 = x.find("\"", index_d + 1)
        test = False

        if index_a == -1:
            test = False

        # elif index_c == -1 and index_d == -1:
        #     return False if 0 <= index_b < index_a else True

        elif index_b != -1:
            test = not (0 <= index_b < index_a)

        elif (not (index_c < index_a < index_c1)) and (index_c > 0 and index_c1 > 0):
            test = True

        elif (not (index_d < index_a < index_d1)) and (index_d > 0 and index_d1 > 0):
            test = True

        elif (index_b == index_c == index_d == -1) and index_a >= 0:
            test = True

        if test:
            self.error_dict[str(line_count) + 'C'] = \
                {'Code': 'S003', 'Message': 'Unnecessary semicolon'}

    def check_comment_spacing(self, x, line_count):
        index_a = x.find("#")
        test = False

        if index_a != -1:
            test = index_a >= 2 and not (x[index_a - 1] == " " and x[index_a - 2] == " ")

        if test:
            self.error_dict[str(line_count) + 'D'] = \
                {'Code': 'S004', 'Message': 'At least two spaces required before inline comments'}

    def find_todo(self, x, line_count):
        x = x.lower()

        index_a = x.find("#")
        index_b = x.find("todo")

        if 0 <= index_a < index_b:
            self.error_dict[str(line_count) + 'E'] = {'Code': 'S005', 'Message': 'TODO found'}

    def check_blanklines(self, x, count, line_count):

        if count > 2 and x != '':
            self.error_dict[str(line_count) + 'F'] = \
                {'Code': 'S006', 'Message': 'More than two blank lines used before this line'}
            count = 0

        return count

    def check_names(self, x, line_count):

        if re.match(r'(def|class)', x) is not None:
            if re.match(r'(def|class) {,1}[\w_]+', x) is None:
                self.error_dict[str(line_count) + 'G'] = \
                    {'Code': 'S007', 'Message': 'Too many spaces after construction_name (def or class)'}

            if re.match(r'^class', x) is not None:
                name_class = re.match(r"^class *([A-Z][a-z]+)+", x)

                if not name_class:
                    self.error_dict[str(line_count) + 'H'] = \
                        {'Code': 'S008', 'Message': "Class name '" + re.findall(r'[A-Za-z_]+', x)[1]
                                                    + "' should be written in CamelCase"}

            else:
                name_function = re.match(r'def *_{,2}([a-z]+[0-9]*_?)+_{,2}', x)

                if not name_function:
                    self.error_dict[str(line_count) + 'I'] = \
                        {'Code': 'S009', 'Message': "Function name '" + re.findall(r'[A-Za-z_]+', x)[1]
                                                    + "' should be written in snake_case"}

    def ast_checks(self):

        script = open(self.file).read()
        tree = ast.parse(script)
        dict_func = {}

        for node in ast.walk(tree):
            # Checking if node in in function state and also recording the start and end pos of functions
            if isinstance(node, ast.FunctionDef):
                self.ast_argument_check(node)
                dict_func[node.name] = {'start': node.lineno, 'end': node.end_lineno}

            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):

                for v in dict_func.values():
                    if v["start"] <= node.lineno <= v["end"]:
                        self.ast_variable_check(node.id, node.lineno)

    def ast_argument_check(self, node):
        arg_name = [a.arg for a in node.args.args]

        # Check for S010 carried out via regex on the argument name
        for element in arg_name:

            name_arg = re.match(r'_{,2}([a-z]+[0-9]*_?)+_{,2}$', element)

            if not name_arg:
                self.error_dict[str(node.lineno) + 'J'] = \
                    {'Code': 'S010', 'Message': "Argument name '" + re.findall(r'[A-Za-z_]+', element)[0]
                                                + "' should be written in snake_case"}

        # Check for S012 carried out to check mutable arguments
        for item in node.args.defaults:
            if isinstance(item, ast.List):

                self.error_dict[str(node.lineno) + 'L'] = \
                    {'Code': 'S012', 'Message': "The default argument value is mutable"}

    def ast_variable_check(self, name, line):
        var_arg = re.match(r'_{,2}([a-z]+[0-9]*_?)+_{,2}$', name)

        if not var_arg:
            self.error_dict[str(line) + 'K'] = \
                {'Code': 'S011', 'Message': "Variable name '" + re.findall(r'[A-Za-z_]+', name)[0]
                                            + "' should be written in snake_case"}

    def print_error_dict(self):
        for k, v in self.error_dict.items():
            print(f'{self.file}: Line {k[:-1]}: {v["Code"]} {v["Message"]}')
