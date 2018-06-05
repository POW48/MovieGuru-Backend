import json

rankdict =  json.load(open('rankdict','r'))
moiveset = json.load(open('movieset','r'))

print(rankdict['死亡'])
a = 1
while a!=0:
    a = input()
    if a in rankdict:
        count = 0
        for i in rankdict[a]:
            print(i[1][1])
            print(moiveset[i[0]])
            count+=1
            if count==10:
                break

    else:
        print('nothing')
# for i in moiveset:
#     for word in moiveset[i]['title']:
#         print(word)

# a = json.load(open('douban/1291544.json','r'))['tags']
# print(json.load(open('douban/1291544.json','r'))['tags'])
