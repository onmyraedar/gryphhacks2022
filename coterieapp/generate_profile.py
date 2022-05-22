import json

#Different categories of YT videos
CategoryDict = {2 : 'Autos & Vehicles', 1:   'Film & Animation', 10 : 'Music', 15 : 'Pets & Animals', 17 : 'Sports', 18 : 'Short Movies', 19 : 'Travel & Events', 20 : 'Gaming', 21 : 'Videoblogging', 22 : 'People & Blogs', 23 : 'Comedy', 24 : 'Entertainment', 25 : 'News & Politics', 26 : 'Howto & Style', 27 : 'Education', 28 : 'Science & Technology', 29 : 'Nonprofits & Activism',30 : 'Movies', 31 : 'Anime/Animation', 32 : 'Action/Adventure', 33 : 'Classics', 34 : 'Comedy', 35 : 'Documentary', 36 : 'Drama', 37 : 'Family', 38 : 'Foreign', 39 : 'Horror', 40 : 'Sci-Fi/Fantasy', 41 : 'Thriller', 42 : 'Shorts', 43 : 'Shows', 44 : 'Trailers'}

def generate_t5_categories(vids_filepath):
    vids_file = open("{}.json".format(vids_filepath))
    data = json.load(vids_file)
    Categorylist = []
    NumberCatfound = {}
    Likedlist1 = []
    for x in data:
        # print(x)
        for video in x:
            snippet_dict = video["snippet"]
            categoryId = snippet_dict["categoryId"]
            vidTitle = snippet_dict["title"]
            Likedlist1.append(vidTitle)
            Categorylist.append(categoryId)
            #print (categoryId)
            #print ('\n')
            #print (Categorylist)
            #print (CategoryDict[26])
    for category in Categorylist:
        NumberCatfound[int(category)] = 0
    for cat in Categorylist:
        NumberCatfound[int(cat)] += 1
        # print ("the category # is: "+ category + " which is : " + CategoryDict[int(category)] + '\n')
    sorted_values = sorted(NumberCatfound.values())
    sorted_values.reverse()
    sorted_dict = {}

    for i in sorted_values:
        for k in NumberCatfound.keys():
            if NumberCatfound[k] == i:
                sorted_dict[k] = NumberCatfound[k]
                break
    topCategory = sorted_dict.keys()

    top5Cat1 = {}
    acc = 1
    for item in topCategory:
        NumberOfvids = sorted_dict[item]
        category = CategoryDict[item]
        top5Cat1[category] = NumberOfvids
        if acc == 5:
            break
        acc += 1
    return top5Cat1

def RelevantSubs(subs_filepath):
    acc = 0
    topYoutube1 = {}
    subs_file = open("{}.json".format(subs_filepath))
    subdata = json.load(subs_file)  
    for x in subdata:
        for item in x:
            acc+=1
            topYoutube1[acc] = item['snippet']['title']
            if acc == 100:
                break
    return topYoutube1