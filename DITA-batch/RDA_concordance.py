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

"""         Find the xref, which is based on the DITA key and the last element of the URI, the xrefID
Find the parent paragraph that contains the xref
Find the sibling div of the parent paragraph
Get id of the div
<div id="be0aa1ca-59c0-49f5-89c6-abf2f139b574">
                <p outputclass="title" id="2ce1ac20-3fec-4fc1-a656-0d440fd17278">
                    <xref outputclass="ps_link"
                     keyref="rdaeP20310/855b7986-9774-4425-8fe3-1bd87814488b">Recording</xref>
                </p>
                
                <div id="cd0b5d7f-bcb8-4fc9-9dff-3fed343b9bc2"/>
            </div>
 """
