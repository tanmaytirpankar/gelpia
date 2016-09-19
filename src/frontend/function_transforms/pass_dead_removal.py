#!/usr/bin/env python3

from pass_utils import *

import collections
import sys


def dead_removal(exp, inputs, assigns, consts=None):
  used_inputs = set()
  used_assigns = set()
  used_consts = set()

  work_stack = list()

  TWO_ITEMS = BINOPS.union({"Tuple"})
  ONE_ITEM  = UNOPS.union({"Return"})
  UNUSED = {"ConstantInterval", "PointInterval", "Float", "Integer"}

  def _dead_removal(exp):
    tag = exp[0]

    if tag == "Variable":
      if exp[1] not in used_assigns:
        used_assigns.add(exp[1])
        work_stack.append(assigns[exp[1]])
      return

    if tag in TWO_ITEMS:
      _dead_removal(exp[1])
      _dead_removal(exp[2])
      return

    if tag == "Const":
      used_consts.add(exp[1])
      return

    if tag == "Input":
      used_inputs.add(exp[1])
      return

    if tag in ONE_ITEM:
      return  _dead_removal(exp[1])

    if tag in UNUSED:
      return

    if tag == "Box":
      for e in exp[1:]:
        _dead_removal(e)
      return

    print("Error unknown in dead_removal: '{}'".format(exp))
    sys.exit(-1)

  _dead_removal(exp)
  while len(work_stack) > 0:
    next_exp = work_stack.pop()
    _dead_removal(next_exp)


  new_inputs = collections.OrderedDict()
  for k in inputs:
    if k in used_inputs:
      new_inputs[k] = inputs[k]

  new_assigns = collections.OrderedDict()
  for k in assigns:
    if k in used_assigns:
      new_assigns[k] = assigns[k]

  if consts == None:
    return new_inputs, new_assigns

  new_consts = collections.OrderedDict()
  for k in consts:
    if k in used_consts:
      new_consts[k] = consts[k]

  return new_inputs, new_assigns, new_consts









def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_simplify import simplify

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  exp, consts = lift_consts(exp, inputs, assigns)
  exp = simplify(exp, inputs, assigns, consts)

  dead_removal(exp, inputs, assigns, consts)

  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_assigns(assigns)
  print()
  print_consts(consts)


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
