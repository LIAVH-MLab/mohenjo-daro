
#%%
import pandas as pd
import seaborn as sns

# %%

pd.set_option('display.max_columns', 1000)
art = pd.read_csv('https://raw.githubusercontent.com/PrattSAVI/LIAVH/master/data/Artifacts.csv',engine='python',encoding="cp1254")

art.head()
# %%

sns.countplot(data=art,orient='v',y='obj_category', color='black',
    order=art.groupby(by='obj_category').size().sort_values(ascending=False).index.tolist())
sns.despine(bottom=True)
plt.grid(axis = "x", color = "grey" , lw = 0.25 , alpha = 0.5)
plt.tick_params(bottom=False)
plt.xlabel("")
plt.ylabel("")
plt.show()

# %%
import matplotlib.pyplot as plt

gr = pd.pivot_table(data=art[['obj_category','obj_time_cat']], index = 'obj_category',columns='obj_time_cat',aggfunc=len)
gr['na'] = gr[ '[check data]' ]
gr = gr.drop(["[no data]",'[check data]'],axis = 1)

ord = art.groupby(by='obj_category').size().sort_values(ascending=True).index.tolist()
gr = gr.reindex( ord )

gr.plot(kind='barh',stacked=True,colormap="tab10")
sns.despine(bottom=True,left=True)
plt.grid(axis = "x", color = "grey" , lw = 0.25 , alpha = 0.5)
plt.tick_params(bottom=False,left=False)
plt.legend( frameon=False)
plt.xlabel("")
plt.ylabel("")
plt.show()

# %%

path = r"C:\Users\csucuogl\Downloads\Wells_and_Water_Features_Refs_Mackay.xlsx"
water = pd.read_excel( path )

grw = pd.pivot_table(data=water[['Feature','Period_cited_in_text']], index = 'Feature',columns='Period_cited_in_text',aggfunc=len)

ord = water.groupby(by='Feature').size().sort_values(ascending=True).index.tolist()
grw = grw.reindex( ord )

grw.plot(kind='barh',stacked=True,colormap="tab10")
sns.despine(bottom=True,left=True)
plt.grid(axis = "x", color = "grey" , lw = 0.25 , alpha = 0.5)
plt.tick_params(bottom=False,left=False)
plt.legend( frameon=False)
plt.xlabel("")
plt.ylabel("")
plt.show()



# %%

path = r"C:\Users\csucuogl\Downloads\Doorsils_and_Floor_Features_Level_Refs_Mackay.xlsx"
floor = pd.read_excel( path )

sns.countplot(data=floor,orient='v',y='Feature', color='black',
    order=floor.groupby(by='Feature').size().sort_values(ascending=False).index.tolist())

sns.despine(bottom=True,left=True)
plt.grid(axis = "x", color = "grey" , lw = 0.25 , alpha = 0.5)
plt.tick_params(bottom=False,left=False)
plt.legend( frameon=False)
plt.xlabel("")
plt.ylabel("")
plt.show()


# %%
