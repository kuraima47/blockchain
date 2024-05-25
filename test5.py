import functools
import sys
import dis
from test6 import abc


def trace_lines(frame, event, arg):
    if event == 'opcode':
        return traces_opcodes
    if event != 'line':
        return
    co = frame.f_code
    func_name = co.co_name
    line_no = frame.f_lineno
    print('*  {} line {}'.format(func_name, line_no))
    return trace_lines


def traces_opcodes(frame, event, arg):
    if event != 'opcode':
        return
    co = frame.f_code
    func_name = co.co_name
    opcode = co.co_code[frame.f_lasti]
    opcode_name = dis.opname[opcode]
    print('*    {} opcode {} ({})'.format(func_name, opcode, opcode_name))
    return traces_opcodes


def trace_calls(frame, event, arg):
    if event == 'opcode':
        return traces_opcodes
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
    return trace_lines


def c(input):
    print('input =', input)
    print('Leaving c()')


def b(arg):
    val = arg * 5
    c(val)
    abc()
    print(len(range(val)))
    print('Leaving b()')


def a():
    b(2)
    print('Leaving a()')


sys._getframe().f_trace_opcodes = True
sys.settrace(trace_calls)
sys._getframe().f_trace = trace_calls
a()
sys.settrace(None)