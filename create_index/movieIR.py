import json
import os

import numpy as np

import jieba
import progressbar
from sklearn import feature_extraction
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

movieset = dict()


def get_stopwordslist(filepath):
    stopwords = [line.strip() for line in open(
        filepath, 'r', encoding='utf-8').readlines()]
    return stopwords

#
# def loadjson():
#     with open('douban/1291543.json', 'r') as f:
#         loaddict = json.load(f)
#         print(loaddict)
#         print(loaddict['title'])
#         print(loaddict['type'])
#         print(loaddict['card_subtitle'])
#         for i in loaddict['actors']:
#             print(i['name'])
#         print(loaddict['genres'])
#         for i in (loaddict['directors']):
#             print(i['name'])
#         print(loaddict['intro'])
#     pass
#
#


def getlistdir(name):
    a = []
    for i in os.listdir(name):
        if os.path.splitext(i)[-1] == '.json':
            a.append(i)

    return a


def gettfidf():
    moivelist = getlistdir('douban')
    print(moivelist)
    count = 0
    for movie in moivelist:
        count = count+1
        with open('douban/'+movie, 'r') as f:
            this_or_moive = json.load(f)
            the = dict()
            the['title'] = this_or_moive['title']
            actors = []
            for act in this_or_moive['actors']:
                actors.append(act['name'])
            the['actors'] = actors
            directors = []

            for director in this_or_moive['directors']:
                directors.append(director['name'])
            the['actors'] = actors
            the['directors'] = directors

            the['intro'] = this_or_moive['intro']
            the['aka'] = this_or_moive['aka']

            tags = []
            for tag in this_or_moive['tags']:
                tags.append(tag['name'])
            the['tags'] = tags
            the['genres'] = this_or_moive['genres']

        thismovie_id = os.path.splitext(movie)[0]
        movieset[thismovie_id] = the
        # if count==100:
        #     break

    json.dump(movieset, open('movieset', 'w', encoding='utf8'))

    stopwordslist = get_stopwordslist('chinese_stopword.txt')
    moive_corpus = []
    name_act_corpus = []
    for i in movieset:
        temp = jieba.cut(movieset[i]['intro'], cut_all=all)
        a = []
        for word in temp:
            # if word not in stopwordslist:
            a.append(word)
        a = ' '.join(a)
        b = movieset[i]['actors']+movieset[i]['directors'] + \
            movieset[i]['tags']+movieset[i]['aka'] + movieset[i]['genres']
        b.append(movieset[i]['title'])

        b = ' '.join(b)
        allnameset = b
        b = jieba.cut(b, cut_all=True)
        b = ' '.join(b)
        b = b+' '+allnameset
        # print(a)
        # print(b)

        moive_corpus.append(a)
        name_act_corpus.append(b)

    # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
    tfidf = transformer.fit_transform(
        vectorizer.fit_transform(moive_corpus))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    intro_word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语
    # weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重

    # print(tfidf.shape[1])
    # c = tfidf[3].toarray()
    # print(c[0][1])
    # # for i in tfidf:
    # #     for j in tfidf:
    # #
    # #         print(type(j))
    # print(len(intro_word))

    # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer2 = CountVectorizer()
    transformer2 = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
    tfidf2 = transformer.fit_transform(
        vectorizer2.fit_transform(name_act_corpus))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    title_word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语
    # weight2 = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    # for i in range(len(weight)):#打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
    #     print ("-------这里输出第",i,u"类文本的词语tf-idf权重------")
    #     for j in range(len(word)):
    #         if weight[i][j]!=0:
    #             print (word[j],weight[i][j] )

    a = 0
    for i in movieset:
        tfidfidct = dict()
        weight = tfidf[a].toarray()
        for j in range(len(intro_word)):

            if weight[0][j] != 0:
                tfidfidct[intro_word[j]] = weight[0][j]
                # print(word[j])
        movieset[i]['tfidf'] = tfidfidct
        a += 1

    # for i in movieset:
    #     print(movieset[i]['intro'])
    #     print(movieset[i]['tfidf'])

    # name 0.25 director 0.2 actors 0.15 tfidf 0.15*tfidf

    rank_dict = dict()
    all_word = intro_word+title_word

    for i in movieset:
        movie = movieset[i]
        all_word.extend(movie['actors'])
        all_word.extend(movie['directors'])
        all_word.append(movie['title'])
        for word in movie['title']:
            if word not in all_word:
                all_word.append(word)
        all_word.extend(movie['tags'])
        all_word.extend(movie['genres'])
        all_word.extend(movie['aka'])
        for aka in movie['aka']:
            for word in aka:
                if word not in all_word:
                    all_word.append(word)

    bar = progressbar.ProgressBar(maxval=len(all_word))
    a = 0
    for word in all_word:
        bar.update(a)
        a = a+1
        rank_dict[word] = dict()
        # title aka tags genres actors directors tf-idf

        for movie in movieset:
            count = 0
            flags = [0, 0, 0, 0, 0, 0, 0]
            flagscount = 0
            movieid = movie
            movie = movieset[movie]

            if word in movie['title']:
                count += 0.25
                flags[flagscount] = 1
            flagscount += 1

            for aka in movie['aka']:
                if word in aka:
                    count += 0.25
                    flags[flagscount] = 1

                    break
            flagscount += 1
            for tag in movie['tags']:
                if word in tag:
                    count += 0.2
                    flags[flagscount] = 1

                    break
            flagscount += 1
            for genre in movie['genres']:
                if word in genre:
                    count += 0.2
                    flags[flagscount] = 1

                    break
            flagscount += 1
            for actor in movie['actors']:
                if word in actor:
                    count += 0.2
                    flags[flagscount] = 1

                    break
            flagscount += 1
            for director in movie['directors']:

                if word in director:
                    flags[flagscount] = 1

                    count += 0.2
                    break

            flagscount += 1
            if word in movie['tfidf']:
                count += movie['tfidf'][word]*0.15
                flags[flagscount] = 1

            flagscount += 1

            # thismoivecount = dict()
            # thismoivecount[movie]  = count
            if count != 0:
                try:
                    temp = []
                    temp.append(count)
                    temp.append(flags)
                    rank_dict[word][movieid] = temp
                except:
                    print('wrong')

        rank_dict[word] = sorted(
            rank_dict[word].items(), key=lambda x: x[1], reverse=True)

    bar.finish()
    json.dump(rank_dict, open('rankdict', 'w', encoding='utf8'))


if __name__ == '__main__':
    # loadjson()
    # getlistdir()
    gettfidf()
