import glob

from lxml import etree
from os import path

print('FileName,Parent_Div_ID,Child_P_ID')

ENTITYCHAPTER = 'Work'

for file in glob.glob(f'C:/Users/bibli/OneDrive/Documents/work/RDA/Entity Chapters/{ENTITYCHAPTER}/*.dita'):
    tree = etree.parse(file)
    divs = tree.xpath('//div[p/@outputclass="title"]')
    
    for div in divs:
        parentid = div.xpath('@id')
        childid = div.xpath('p[@outputclass="title"]/@id')
        if len(childid) > 1:
            print(f"I didn't expect there to be more than one child <p> tag for parent: {parentid[0]}")
        elif len(childid) == 0:
            print(f"I didn't expect an empty child: {parentid[0]}")
        else:    
            print(f'{path.basename(file)},{parentid[0]},{childid[0]}')
