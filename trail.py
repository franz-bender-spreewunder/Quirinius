from ir_dataset import IRDataSet

x = IRDataSet()

y = x.get_unlabeled_in_range()

print(len(list(y)))
