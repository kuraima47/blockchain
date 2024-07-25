# smart_contract.py
import json
import importlib.util
import pickle
import sys
import dis


class Contract:

    def __init__(self):
        data = json.loads(open('contract/contract.json').read())
        params = json.loads(open('params.json').read())
        self.main = data['project_main']
        self.path = f"contract/{self.main}"
        self.contract = None
        self.func = params["callable_function"]

    def init(self):
        spec = importlib.util.spec_from_file_location("smart_contract", self.path)
        self.contract = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.contract)

    def load_state(self):
        try:
            with open('state.pkl', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    def set_state(self, state):
        for k, v in state.items():
            setattr(self.contract, k, v)

    def save_state(self):
        state_vars = vars(self.contract)
        with open('state.pkl', 'wb') as f:
            pickle.dump(state_vars, f)

    def execute(self, func_name, *args):
        sys._getframe().f_trace_opcodes = True
        sys.settrace(self.__trace_calls)
        sys._getframe().f_trace = self.__trace_calls
        try:
            getattr(self.contract, func_name)(*args)
        except Exception as e:
            print(f"Error during execution: {e}")
        sys.settrace(None)

    def __trace_lines(self, frame, event, arg):
        if event == 'opcode':
            return self.__traces_opcodes
        if event != 'line':
            return
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        print('*  {} line {}'.format(func_name, line_no))
        return self.__trace_lines

    def __traces_opcodes(self, frame, event, arg):
        if event != 'opcode':
            return
        co = frame.f_code
        func_name = co.co_name
        opcode = co.co_code[frame.f_lasti]
        opcode_name = dis.opname[opcode]
        print('*Infos : {} opcode {} ({})'.format(func_name, opcode, opcode_name))
        return self.__traces_opcodes

    def __trace_calls(self, frame, event, arg):
        if event == 'opcode':
            return self.__traces_opcodes
        elif event != 'call':
            return
        co = frame.f_code
        func_name = co.co_name
        if func_name == 'write':
            return
        line_no = frame.f_lineno
        filename = co.co_filename
        print('* Call to {} on line {} of {}'.format(func_name, line_no, filename))
        frame.f_trace_opcodes = True
        return self.__trace_lines


if __name__ == "__main__":
    contract = Contract()
    contract.init()
    state = contract.load_state()
    if state is not None:
        contract.set_state(state)
    contract.execute(contract.func, 1, 2, 3)
