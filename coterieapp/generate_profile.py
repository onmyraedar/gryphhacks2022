import json

#Different categories of YT videos
CategoryDict = {2 : 'Autos & Vehicles', 1:   'Film & Animation', 10 : 'Music', 15 : 'Pets & Animals', 17 : 'Sports', 18 : 'Short Movies', 19 : 'Travel & Events', 20 : 'Gaming', 21 : 'Videoblogging', 22 : 'People & Blogs', 23 : 'Comedy', 24 : 'Entertainment', 25 : 'News & Politics', 26 : 'Howto & Style', 27 : 'Education', 28 : 'Science & Technology', 29 : 'Nonprofits & Activism',30 : 'Movies', 31 : 'Anime/Animation', 32 : 'Action/Adventure', 33 : 'Classics', 34 : 'Comedy', 35 : 'Documentary', 36 : 'Drama', 37 : 'Family', 38 : 'Foreign', 39 : 'Horror', 40 : 'Sci-Fi/Fantasy', 41 : 'Thriller', 42 : 'Shorts', 43 : 'Shows', 44 : 'Trailers'}

#Generates the user's top 5 categories
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

#Generates a list of the user's liked videos
def generate_liked_vids(vids_filepath):
    vids_file = open("{}.json".format(vids_filepath))
    data = json.load(vids_file)
    Likedict = {}
    for x in data:
        for video in x:
            snippet_dict = video["snippet"]
            categoryId = snippet_dict["categoryId"]
            vidTitle = snippet_dict["title"]
            Likedict[vidTitle] = [video["id"], categoryId]
    return Likedict

def RelevantSubs(subs_filepath):
    acc = 0
    topYoutube1 = {}
    subs_file = open("{}.json".format(subs_filepath))
    subdata = json.load(subs_file)  
    for x in subdata:
        for item in x:
            acc+=1
            topYoutube1[item['snippet']['title']] = 'https://www.youtube.com/channel/'+item['snippet']['resourceId']['channelId']
            if acc == 100:
                break
    return topYoutube1

def compareSubs(user1subs_filepath, user2subs_filepath):
    topYoutubeCommon = []
    topYoutube1 = RelevantSubs(user1subs_filepath)
    topYoutube2 = RelevantSubs(user2subs_filepath)
    print(topYoutube1)
    for channel in topYoutube1.keys():
        for channel2 in topYoutube2.keys():
            if channel == channel2:
                topYoutubeCommon.append(channel)
    return topYoutubeCommon

def compareLikes(user1vids_filepath, user2vids_filepath):
    topLikeCommon = []
    Likedlist1 = generate_liked_vids(user1vids_filepath)#('speedo3133755de2664b819a13198325c366edvids.json')
    Likedlist2 = generate_liked_vids(user2vids_filepath)#('sphenic8c82df195bd04699b5411acb300510aevids.json')
    for vid in Likedlist1:
        for vid2 in Likedlist2:
            if vid == vid2:
                topLikeCommon.append(vid)
    return topLikeCommon
    
def videorecs(user1vids_filepath, user2vids_filepath):
    topCat1 = generate_t5_categories(user1vids_filepath)
    topcat = list(topCat1.keys())[0]
    topcatnum = 0
    for key in CategoryDict:
        if CategoryDict[key] == topcat:
            topcatnum = key
    Likedict2 = generate_liked_vids(user2vids_filepath)
    Videorecs = {}
    for key in Likedict2.keys():
        catid = int(Likedict2[key][1])
        vidid = str(Likedict2[key][0])
        if catid == topcatnum:
            Videorecs[key] = 'https://www.youtube.com/watch?v='+vidid
    return Videorecs