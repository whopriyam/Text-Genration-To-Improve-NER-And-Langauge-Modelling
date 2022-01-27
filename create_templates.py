import pandas as pd
data = pd.read_csv("ner_dataset.csv", encoding= 'unicode_escape')
#Removing BIO tags
data["Tag"] = data["Tag"].str.replace("B-", "")

data["Tag"] = data["Tag"].str.replace("I-", "")

#Removing .
data = data[~data["Word"].isin(["."])]
data = data.reset_index(inplace = False,drop=True)
data.to_csv("Interim.csv")


data2 = pd.DataFrame(columns=["Sentence #","Word","Tag"])

c = 1
new_ind = 2
sentence_str = data.at[0,"Word"] + " "
tag_temp = data.at[0,"Tag"]

#data2.at[0,"Word"] = data.at[0,"Word"] 
#data2.at[0,"Tag"] = data.at[0,"Tag"]
for i in range(0,len(data)):
    print (str(i))
    if "Sentence" not in str(data.at[i,"Sentence #"]) and i !=0:
        if tag_temp == data.at[i,"Tag"]:
            sentence_str = sentence_str + data.at[i,"Word"] + " "
        else:
            data2.at[c,"Word"] = sentence_str
            data2.at[c,"Tag"] = tag_temp
            sentence_str = data.at[i,"Word"] + " "
            tag_temp = data.at[i,"Tag"]
            c = c+1
    
    elif i !=0 and i!=len(data)-1:
        data2.at[c,"Word"] = sentence_str
        data2.at[c,"Tag"] = data.at[i-1,"Tag"]
        data2.at[c+1,"Sentence #"] = "Sentence: " + str(new_ind)
        # data2.at[c,"Word"] = sentence_str
        # data2.at[c,"Tag"] = data.at[i,"Tag"]
        new_ind = new_ind+1
        sentence_str = data.at[i,"Word"] + " "
        c = c+1
    
    if i == len(data)-1:
        data2.at[c,"Word"] = sentence_str
        data2.at[c,"Tag"] = data.at[i,"Tag"]    
        if "Sentence" in str(data.at[i,"Sentence #"]):
            data2.at[c,"Sentence #"] = data.at[i,"Sentence #"]
    print (sentence_str)
        



data2 = data2.reset_index(inplace = False,drop=True)
data2.at[0,"Sentence #"] = "Sentence: 1"

data2.to_csv("Test2.csv")

data = data2


#Getting list of tags
tags = list(data['Tag'].unique())
print (tags)

#Removing O tags
tags.remove("O")
print (tags)

#Getting list of keywords for each tag
tag_dict = {}
for tag in tags:
    temp_data = data[data["Tag"].isin([tag])]
    tag_dict[tag] = list(set(temp_data["Word"]))

import json
with open('tags_list.json', 'w') as fp:
    json.dump(tag_dict, fp)


#Exporting the txt files for keywords corresponding to each tag
for k,v in tag_dict.items():
    with open("txt_resources/"+str(k)+".txt", 'w') as output:
        for row in v:
            output.write(str(row) + '\n')

#Formatting the tags and adding sentence number
sentence_num = data.at[0,"Sentence #"]
for i in data.index:
    if data.at[i,"Tag"] in tags:
        tag = data.at[i,"Tag"]
        print (i)
        print (str(tag))
        temp_tag = ' " <'+str(tag)+'> " ' + "Var_"+str(tag)+ ' " </'+tag+'> "' 
        data.at[i,"Word"] = temp_tag
        if (i%10==0):
            print(temp_tag)
    
    if len(str(data.at[i,"Sentence #"])) != 3:
        sentence_num = data.at[i,"Sentence #"]
    else:
        data.at[i,"Sentence #"] = sentence_num

data.to_csv("data_tag_transformed.csv",index=False)

#Total 47959 sentences
sentence_list = []

#Creating the templates
for i in range(1,new_ind):
    sentence = ""
    temp_data = data[data["Sentence #"].isin(["Sentence: "+str(i)])]
    word_list = list(temp_data["Word"])
    print (word_list)
    for word in word_list:
        if "</" not in word:
            sentence = sentence + ' " <O> ' +word+' </O> "'
        else:
            sentence = sentence + word
    
    sentence_list.append(sentence)
    print (sentence)

print (sentence_list[0])

with open("templates_gen.txt", 'w') as output:
    for i in range(0,len(sentence_list)):
        if i != len(sentence_list)-1:
            output.write(sentence_list[i] + " | " +'\n' + '\n')
        else:
            output.write(sentence_list[i] + "; ")

#47960