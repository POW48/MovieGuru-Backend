import jieba

a = ['fae','fae']
b = ['fae','fae']

b = jieba.cut('此间的少年', cut_all=True)
b = ' '.join(b)

print(b)