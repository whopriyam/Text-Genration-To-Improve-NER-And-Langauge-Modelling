'''
The purpose of this script is to generate augmentations of input text using Pegasus.

Created by Priyam Basu (July-Dec 2022)

'''


import pandas as pd
import time
import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import re

data = pd.read_csv("data/GMB_train.csv",encoding='unicode_escape')

#Removing B-I tags and full stop
data["Tag"] = data["Tag"].str.replace("B-", "")
data["Tag"] = data["Tag"].str.replace("I-", "")

data = data[~data["Word"].isin(["."])]
data = data.reset_index(inplace = False,drop=True)


#Adding correct sentence numbers
sentence_num = data.at[0,"Sentence #"]
for i in data.index:
    
    if len(str(data.at[i,"Sentence #"])) != 3:
        sentence_num = data.at[i,"Sentence #"]
    else:
        data.at[i,"Sentence #"] = sentence_num


#PEGASUS Transformer model
model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

 
#Setting up the model
def get_response(input_text,num_return_sequences):
  batch = tokenizer.prepare_seq2seq_batch([input_text],truncation=True,padding='longest',max_length=60, return_tensors="pt").to(torch_device)
  translated = model.generate(**batch,max_length=60,num_beams=10, num_return_sequences=num_return_sequences, temperature=1.5)
  tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
  return tgt_text

col_list = ["Sentence #","Original_Sentence","T1","T2","T3","T4","T5"]
data2 = pd.DataFrame(columns=col_list)


#Generating augmentations
time1 = time.time()
c = 0

for i in range(1,47960):
    if (i%20 == 0):
        print (str(i)," texts done.")
    temp_data = data[data["Sentence #"].isin(["Sentence: "+ "% s" % i])]
    word_list = temp_data["Word"].to_list()
    sentence = " ".join(word_list)
    
    #print (sentence)

    t_list = (get_response(sentence, 5))
    #print (t_list)
    
    temp_data2 = temp_data[~temp_data["Tag"].isin(["O"])]
    temp_data2 = temp_data2.reset_index(inplace = False,drop=True)
    #print(temp_data2)
    
    final_list = []
    
    
    for item in t_list:
        #print (item)
        str1 = ""
        item = list(item.split(" "))
        for term in item:
            term = re.sub(r'[.]', '', term)
            temp_data3 = temp_data2[temp_data2["Word"].isin([term])]
            #print (term)
            temp_data3 = temp_data3.reset_index(inplace = False,drop=True)
            #print (temp_data3)
            if len(temp_data3) != 0:
                #print("Check1")
#                 print(temp_data3)
#                 print (term)
                str1 = str1 + "<" + temp_data3.at[0,"Tag"] + "> " + temp_data3.at[0,"Word"] + " </" + temp_data3.at[0,"Tag"] + "> "
            else:
                #print ("Check2")
                str1 = str1 + term + " "
        final_list.append(str1)
    
    data2.at[c,"Sentence #"] = "Sentence: "+ "% s" % i
    data2.at[c,"Original_Sentence"] = sentence
    for j in range (1,6):
        #print (c)
        data2.at[c,"T"+ "% s" % j] = final_list[j-1]
    c = c+1
    
time2 = time.time()
print ((time2-time1))

data2.to_csv("Pegasus_augmentations.csv")