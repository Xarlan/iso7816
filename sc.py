import iso7816

my_card = iso7816.Iso7816()

reader = my_card.get_readers()  # get avaible readres

print(reader)

my_card.connect(reader[1])
# my_card.connect(reader[0])

print(my_card.get_atr())

print(my_card.analyze_atr(my_card.get_atr()))


# tmp = ['a', 'b', '', '', 'c', 'd', '']
# print(tmp)
# print(list(filter(None, tmp)))